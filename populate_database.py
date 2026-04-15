import requests
import time
import psycopg2
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DSN = "postgresql://postgres:123456@localhost:5432/animehako"
JIKAN_BASE = "https://api.jikan.moe/v4"
REQUEST_DELAY = 1.5

session = requests.Session()
retry = Retry(total=5, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

def fetch_json(url, timeout=60):
    for attempt in range(8):
        try:
            response = session.get(url, timeout=timeout)
            if response.status_code == 429:
                wait_time = int(response.headers.get('Retry-After', 120))
                print(f"  Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            if response.status_code == 500:
                print(f"  Server error, retrying...")
                time.sleep(5)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  Attempt {attempt + 1}/8 failed: {type(e).__name__}")
            if attempt < 7:
                time.sleep(min(60, 3 ** attempt))
            else:
                return None

def slugify(text):
    if not text:
        return None
    return re.sub(r'[^a-zA-Z0-9_]', '', text.lower().replace(' ', '_').replace("'", ""))

def clear_database(conn):
    print("\n[0/6] Clearing database...")
    cursor = conn.cursor()
    cursor.execute("TRUNCATE anime_tags, anime_genres, screenshots, reviews, tags, genres, anime RESTART IDENTITY CASCADE")
    conn.commit()
    print("  Database cleared")

def load_genres(conn):
    print("\n[1/6] Loading genres...")
    data = fetch_json(f"{JIKAN_BASE}/genres/anime")
    if not data or "data" not in data:
        print("  Failed to load genres")
        return {}

    genres = {}
    cursor = conn.cursor()
    for genre in data["data"]:
        gid = genre["mal_id"]
        name = genre["name"]
        slug = slugify(name)
        cursor.execute(
            "INSERT INTO genres (id, name, slug) VALUES (%s, %s, %s) "
            "ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, slug = EXCLUDED.slug",
            (gid, name, slug)
        )
        genres[gid] = name

    conn.commit()
    print(f"  Loaded {len(genres)} genres")
    return genres

def load_anime(conn, genres, limit=50):
    print(f"\n[2/6] Loading top-{limit} anime...")

    all_anime = []
    page = 1

    while len(all_anime) < limit:
        url = f"{JIKAN_BASE}/top/anime?page={page}&limit=25"
        print(f"  Fetching page {page}...")
        data = fetch_json(url)
        if not data or "data" not in data:
            break

        for anime in data["data"]:
            if len(all_anime) >= limit:
                break
            all_anime.append(anime)

        pagination = data.get("pagination", {})
        if not pagination.get("has_next_page"):
            break
        page += 1
        time.sleep(REQUEST_DELAY)

    print(f"  Fetched {len(all_anime)} anime entries")
    if not all_anime:
        return []

    print("\n[3/6] Saving anime to database...")
    cursor = conn.cursor()
    saved_ids = []

    for i, anime in enumerate(all_anime):
        try:
            mal_id = anime["mal_id"]
            title = anime.get("title", "Unknown")
            title_en = anime.get("title_english")
            title_jp = anime.get("title_japanese")
            poster = anime.get("images", {}).get("jpg", {}).get("image_url")
            cover = anime.get("images", {}).get("jpg", {}).get("large_image_url")
            description = anime.get("synopsis")
            rating = anime.get("score")
            year = anime.get("year")

            season = anime.get("season")
            status_map = {
                "Currently Airing": "airing",
                "Finished Airing": "finished",
                "Not Yet Aired": "upcoming",
                "Hiatus": "hiatus"
            }
            status_db = status_map.get(anime.get("status"))

            episodes = anime.get("episodes") or 0
            duration = anime.get("duration", "")
            if duration:
                match = re.search(r'(\d+)', duration)
                duration = int(match.group(1)) if match else None

            studio = None
            studios = anime.get("studios", [])
            if studios:
                studio = studios[0].get("name")

            cursor.execute("""
                INSERT INTO anime (title, title_en, title_jp, poster, cover, description,
                rating, year, season, status, episodes, duration, studio, external_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (title, title_en, title_jp, poster, cover, description,
                  rating, year, season, status_db, episodes, duration, studio, str(mal_id)))
            result = cursor.fetchone()
            db_id = result[0] if result else mal_id
            saved_ids.append((db_id, mal_id))

            for genre in anime.get("genres", []):
                gid = genre["mal_id"]
                if gid in genres:
                    cursor.execute("""
                        INSERT INTO anime_genres (anime_id, genre_id)
                        VALUES (%s, %s) ON CONFLICT DO NOTHING
                    """, (db_id, gid))

            print(f"  [{i+1}/{len(all_anime)}] {title[:50]}...")
            time.sleep(REQUEST_DELAY)

        except Exception as e:
            print(f"  Error saving anime '{title}': {e}")
            continue

    conn.commit()
    print(f"  Saved {len(saved_ids)} anime")
    return saved_ids

def load_tags_and_reviews(conn, anime_ids):
    print(f"\n[4/6] Loading tags...")
    cursor = conn.cursor()
    tags_cache = {}
    tags_added = 0

    for db_id, mal_id in anime_ids[:30]:
        print(f"  Loading anime #{mal_id}...")
        data = fetch_json(f"{JIKAN_BASE}/anime/{mal_id}")
        if not data or "data" not in data:
            time.sleep(REQUEST_DELAY)
            continue

        anime_data = data["data"]

        for theme in anime_data.get("themes", []):
            name = theme.get("name")
            if not name:
                continue
            slug = slugify(name)

            if slug not in tags_cache:
                cursor.execute("""
                    INSERT INTO tags (name, slug) VALUES (%s, %s)
                    ON CONFLICT (name) DO UPDATE SET slug = EXCLUDED.slug
                    RETURNING id
                """, (name, slug))
                result = cursor.fetchone()
                tags_cache[slug] = result[0] if result else None

            tag_id = tags_cache.get(slug)
            if tag_id:
                cursor.execute("""
                    INSERT INTO anime_tags (anime_id, tag_id) VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (db_id, tag_id))
                tags_added += 1

        for review in anime_data.get("reviews", [])[:2]:
            try:
                user = review.get("user", {})
                author = user.get("username", "Anonymous")
                cursor.execute("""
                    INSERT INTO reviews (anime_id, author_name, title, content, score, external_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (db_id, author[:255], review.get("title", "")[:255],
                      review.get("content", ""), review.get("score"), str(review.get("mal_id", ""))))
            except:
                pass

        for pic in anime_data.get("pictures", [])[:4]:
            url = pic.get("jpg", {}).get("image_url")
            if url:
                cursor.execute("""
                    INSERT INTO screenshots (anime_id, url) VALUES (%s, %s)
                """, (db_id, url))

        conn.commit()
        time.sleep(REQUEST_DELAY)

    print(f"  Loaded {len(tags_cache)} tags, {tags_added} relations")

def main():
    print("=" * 60)
    print("ANIMEHAKO DATABASE POPULATION VIA JIKAN API")
    print("=" * 60)

    try:
        conn = psycopg2.connect(DSN)
        print(f"\nConnected to: animehako")
    except Exception as e:
        print(f"DB connection error: {e}")
        return

    try:
        clear_database(conn)
        genres = load_genres(conn)
        anime_ids = load_anime(conn, genres, limit=50)
        load_tags_and_reviews(conn, anime_ids)

        print("\n" + "=" * 60)
        print("POPULATION COMPLETE!")
        print("=" * 60)
    except Exception as e:
        print(f"\nError: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("\nDB connection closed")

if __name__ == "__main__":
    main()