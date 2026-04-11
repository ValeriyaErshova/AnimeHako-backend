import requests
import time
import psycopg2
import re

DSN = "postgresql://postgres:123456@localhost:5432/animehako"
JIKAN_BASE = "https://api.jikan.moe/v4"
REQUEST_DELAY = 0.5

def fetch_json(url):
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  Ошибка запроса (попытка {attempt + 1}): {e}")
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                return None

def load_genres(conn):
    print("\n[1/4] Загрузка жанров...")
    data = fetch_json(f"{JIKAN_BASE}/genres/anime")
    if not data or "data" not in data:
        print("  Не удалось загрузить жанры")
        return {}
    
    genres = {}
    cursor = conn.cursor()
    for genre in data["data"]:
        genre_id = genre["mal_id"]
        name = genre["name"]
        slug = name.lower().replace(" ", "_").replace("'", "")
        cursor.execute(
            "INSERT INTO genres (id, name, slug) VALUES (%s, %s, %s) "
            "ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, slug = EXCLUDED.slug",
            (genre_id, name, slug)
        )
        genres[genre_id] = name
        print(f"  - {name}")
    
    conn.commit()
    print(f"  Загружено {len(genres)} жанров")
    return genres

def load_top_anime(conn, genres, limit=50):
    print(f"\n[2/5] Загрузка топ-{limit} аниме...")
    anime_list = []
    page = 1
    
    while len(anime_list) < limit:
        print(f"  Загрузка страницы {page}...")
        data = fetch_json(f"{JIKAN_BASE}/top/anime?page={page}")
        if not data or "data" not in data:
            break
        
        for anime in data["data"]:
            if len(anime_list) >= limit:
                break
            anime_list.append(anime)
        
        if not data.get("pagination", {}).get("has_next_page"):
            break
        page += 1
        time.sleep(REQUEST_DELAY)
    
    cursor = conn.cursor()
    loaded_count = 0
    
    for anime in anime_list:
        mal_id = anime["mal_id"]
        title = anime.get("title", "Unknown")
        title_en = anime.get("title_english")
        title_jp = anime.get("title_japanese")
        poster = anime.get("images", {}).get("jpg", {}).get("image_url")
        cover = anime.get("images", {}).get("jpg", {}).get("large_image_url")
        description = anime.get("synopsis")
        rating = anime.get("score")
        year = anime.get("year")
        
        season = None
        status_db = None
        if anime.get("season"):
            season = anime["season"]
        if anime.get("status"):
            status_map = {
                "Currently Airing": "airing",
                "Finished Airing": "finished",
                "Not Yet Aired": "upcoming"
            }
            status_db = status_map.get(anime["status"])
        
        episodes = anime.get("episodes") or 0
        duration = anime.get("duration", "")
        if duration:
            match = re.search(r'(\d+)', duration)
            duration = int(match.group(1)) if match else None
        
        studio = None
        studios = anime.get("studios", [])
        if studios:
            studio = studios[0].get("name")
        
        cursor.execute(
            "INSERT INTO anime (id, title, title_en, title_jp, poster, cover, description, "
            "rating, year, season, status, episodes, duration, studio, external_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            "ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title",
            (mal_id, title, title_en, title_jp, poster, cover, description,
             rating, year, season, status_db, episodes, duration, studio, str(mal_id))
        )
        
        for genre in anime.get("genres", []):
            genre_id = genre["mal_id"]
            if genre_id in genres:
                cursor.execute(
                    "INSERT INTO anime_genres (anime_id, genre_id) VALUES (%s, %s) "
                    "ON CONFLICT (anime_id, genre_id) DO NOTHING",
                    (mal_id, genre_id)
                )
        
        loaded_count += 1
        print(f"  [{loaded_count}/{limit}] {title}")
        time.sleep(REQUEST_DELAY)
    
    conn.commit()
    print(f"  Загружено {loaded_count} аниме")
    return [a["mal_id"] for a in anime_list]

def load_tags(conn, anime_ids):
    print(f"\n[3/5] Загрузка тегов...")
    cursor = conn.cursor()
    tags = {}
    tags_loaded = 0
    
    for i, mal_id in enumerate(anime_ids):
        print(f"  Загрузка тегов для anime #{mal_id} ({i+1}/{len(anime_ids)})...")
        data = fetch_json(f"{JIKAN_BASE}/anime/{mal_id}")
        if not data or "data" not in data:
            continue
        
        anime_data = data["data"]
        for theme in anime_data.get("themes", []):
            theme_name = theme.get("name")
            if not theme_name:
                continue
            theme_slug = theme_name.lower().replace(" ", "_").replace("'", "")
            
            if theme_slug not in tags:
                cursor.execute(
                    "INSERT INTO tags (name, slug) VALUES (%s, %s) "
                    "ON CONFLICT (name) DO UPDATE SET slug = EXCLUDED.slug "
                    "RETURNING id",
                    (theme_name, theme_slug)
                )
                result = cursor.fetchone()
                tags[theme_slug] = result[0] if result else None
            
            tag_id = tags.get(theme_slug)
            if tag_id:
                cursor.execute(
                    "INSERT INTO anime_tags (anime_id, tag_id) VALUES (%s, %s) "
                    "ON CONFLICT (anime_id, tag_id) DO NOTHING",
                    (mal_id, tag_id)
                )
                tags_loaded += 1
        
        time.sleep(REQUEST_DELAY)
    
    conn.commit()
    print(f"  Загружено {len(tags)} тегов, {tags_loaded} связей")
    return tags

def load_reviews(conn, anime_ids):
    print(f"\n[4/5] Загрузка рецензий...")
    cursor = conn.cursor()
    reviews_loaded = 0
    
    for i, mal_id in enumerate(anime_ids[:20]):
        print(f"  Загрузка рецензий для anime #{mal_id} ({i+1}/20)...")
        data = fetch_json(f"{JIKAN_BASE}/anime/{mal_id}/reviews")
        if not data or "data" not in data:
            continue
        
        for review in data["data"][:3]:
            author = review.get("user", {})
            author_name = author.get("username", "Anonymous")
            review_id = review["mal_id"]
            review_title = review.get("title", "")[:255]
            content = review.get("content", "")
            score = review.get("score")
            
            cursor.execute(
                "INSERT INTO reviews (id, anime_id, author_name, title, content, score, external_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (id) DO UPDATE SET author_name = EXCLUDED.author_name",
                (review_id, mal_id, author_name, review_title, content, score, str(review_id))
            )
            reviews_loaded += 1
        
        time.sleep(REQUEST_DELAY)
    
    conn.commit()
    print(f"  Загружено {reviews_loaded} рецензий")

def load_screenshots(conn, anime_ids):
    print(f"\n[5/5] Загрузка скриншотов...")
    cursor = conn.cursor()
    screenshots_loaded = 0
    
    for i, mal_id in enumerate(anime_ids[:20]):
        print(f"  Загрузка скриншотов для anime #{mal_id} ({i+1}/20)...")
        data = fetch_json(f"{JIKAN_BASE}/anime/{mal_id}/pictures")
        if not data or "data" not in data:
            continue
        
        for pic in data["data"][:5]:
            pic_url = pic.get("jpg", {}).get("image_url")
            if pic_url:
                cursor.execute(
                    "INSERT INTO screenshots (anime_id, url) VALUES (%s, %s)",
                    (mal_id, pic_url)
                )
                screenshots_loaded += 1
        
        time.sleep(REQUEST_DELAY)
    
    conn.commit()
    print(f"  Загружено {screenshots_loaded} скриншотов")

def clear_database(conn):
    print("\nОчистка базы данных...")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM anime_tags")
    cursor.execute("DELETE FROM anime_genres")
    cursor.execute("DELETE FROM screenshots")
    cursor.execute("DELETE FROM reviews")
    cursor.execute("DELETE FROM anime")
    cursor.execute("DELETE FROM tags")
    cursor.execute("ALTER SEQUENCE anime_id_seq RESTART WITH 1")
    conn.commit()
    print("База данных очищена")

def main():
    print("=" * 60)
    print("ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ ANIMEHAKO ЧЕРЕЗ JIKAN API")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(DSN)
        print(f"\nПодключено к БД: animehako")
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return
    
    try:
        clear_database(conn)
        genres = load_genres(conn)
        anime_ids = load_top_anime(conn, genres, limit=50)
        load_tags(conn, anime_ids)
        load_reviews(conn, anime_ids)
        load_screenshots(conn, anime_ids)
        
        print("\n" + "=" * 60)
        print("ЗАПОЛНЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("=" * 60)
    finally:
        conn.close()
        print("\nСоединение с БД закрыто")

if __name__ == "__main__":
    main()