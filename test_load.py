import requests
import time
import psycopg2
import re

DSN = "postgresql://postgres:123456@localhost:5432/animehako"
REQUEST_DELAY = 2

def test_api():
    print("Testing API connectivity...")
    import socket
    try:
        socket.setdefaulttimeout(30)
        r = requests.get("https://api.jikan.moe/v4/top/anime?page=1&limit=1", timeout=60)
        print(f"Status: {r.status_code}, Content length: {len(r.text)}")
        if r.status_code == 200:
            data = r.json()
            print(f"Data keys: {list(data.keys())}")
            print(f"Anime count: {len(data.get('data', []))}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

    try:
        r2 = requests.get("https://api.jikan.moe/v4/genres/anime", timeout=60)
        print(f"Genres status: {r2.status_code}")
    except Exception as e:
        print(f"Genres error: {type(e).__name__}: {e}")

def slugify(text):
    if not text:
        return None
    return re.sub(r'[^a-zA-Z0-9_]', '', text.lower().replace(' ', '_').replace("'", ""))

def fetch_json(url, timeout=60):
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200:
                return r.json()
            print(f"HTTP {r.status_code}, retry {attempt+1}/3")
        except Exception as e:
            print(f"Error: {type(e).__name__}, retry {attempt+1}/3")
        time.sleep(5)
    return None

def main():
    test_api()
    
    print("\nConnecting to database...")
    try:
        conn = psycopg2.connect(DSN)
        cur = conn.cursor()
    except Exception as e:
        print(f"DB connection error: {e}")
        return

    print("\nClearing tables...")
    cur.execute("TRUNCATE anime_tags, anime_genres, screenshots, reviews, tags, genres, anime RESTART IDENTITY CASCADE")
    conn.commit()

    print("\nLoading genres...")
    data = fetch_json("https://api.jikan.moe/v4/genres/anime")
    if data and "data" in data:
        for g in data["data"]:
            cur.execute("INSERT INTO genres (id, name, slug) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", 
                       (g["mal_id"], g["name"], slugify(g["name"])))
        conn.commit()
        print(f"  Loaded {len(data['data'])} genres")
    else:
        print("  Failed to load genres")
        return

    print("\nLoading anime (page 1)...")
    data = fetch_json("https://api.jikan.moe/v4/top/anime?page=1&limit=25")
    if not data or "data" not in data:
        print("  Failed to load anime")
        return
    
    anime_list = data["data"]
    print(f"  Got {len(anime_list)} anime")

    for i, anime in enumerate(anime_list):
        try:
            title = anime.get("title", "Unknown")
            poster = anime.get("images", {}).get("jpg", {}).get("image_url")
            cover = anime.get("images", {}).get("jpg", {}).get("large_image_url")
            rating = anime.get("score")
            year = anime.get("year")
            episodes = anime.get("episodes") or 0
            status_map = {"Currently Airing": "airing", "Finished Airing": "finished", "Not Yet Aired": "upcoming"}
            status = status_map.get(anime.get("status"))

            cur.execute("""
                INSERT INTO anime (title, poster, cover, rating, year, status, episodes, external_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (title[:255], poster, cover, rating, year, status, episodes, str(anime["mal_id"])))
            db_id = cur.fetchone()[0]

            for g in anime.get("genres", []):
                cur.execute("INSERT INTO anime_genres (anime_id, genre_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                           (db_id, g["mal_id"]))

            print(f"  [{i+1}/25] {title[:40]}...")
            conn.commit()
            time.sleep(REQUEST_DELAY)
        except Exception as e:
            print(f"  Error: {e}")
            continue

    cur.execute("SELECT COUNT(*) FROM anime")
    print(f"\nTotal anime in DB: {cur.fetchone()[0]}")
    conn.close()

if __name__ == "__main__":
    main()