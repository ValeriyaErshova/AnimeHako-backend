import requests
import time
import psycopg2
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DSN = "postgresql://postgres:123456@localhost:5432/animehako"
JIKAN_BASE = "https://api.jikan.moe/v4"

conn = psycopg2.connect(DSN)
cursor = conn.cursor()

cursor.execute("SELECT external_id FROM anime")
existing_ids = set(str(row[0]) for row in cursor.fetchall())
print(f"Existing: {len(existing_ids)}")

cursor.execute("SELECT id FROM genres")
genre_ids = set(row[0] for row in cursor.fetchall())

status_map = {
    "Currently Airing": "airing",
    "Finished Airing": "finished",
    "Not Yet Aired": "upcoming",
    "Hiatus": "hiatus"
}

count_added = 0
page = 2

while count_added < 50 and page < 20:
    print(f"Fetching page {page}...", flush=True)
    try:
        r = requests.get(f"{JIKAN_BASE}/top/anime?page={page}&limit=25", timeout=60)
        print(f"  Status: {r.status_code}", flush=True)
        if r.status_code != 200:
            time.sleep(10)
            page += 1
            continue
        data = r.json()
        
        for anime in data.get("data", []):
            mal_id = str(anime["mal_id"])
            if mal_id in existing_ids:
                continue
            
            title = anime.get("title") or "Unknown"
            title_en = anime.get("title_english")
            title_jp = anime.get("title_japanese")
            poster = anime.get("images", {}).get("jpg", {}).get("image_url")
            cover = anime.get("images", {}).get("jpg", {}).get("large_image_url")
            description = anime.get("synopsis")
            rating = anime.get("score")
            year = anime.get("year")
            season = anime.get("season")
            status_db = status_map.get(anime.get("status"))
            episodes = anime.get("episodes") or 0
            duration_str = anime.get("duration") or ""
            duration = None
            if duration_str:
                m = re.search(r'(\d+)', duration_str)
                if m:
                    duration = int(m.group(1))
            studio = None
            if anime.get("studios"):
                studio = anime["studios"][0].get("name")

            cursor.execute("""
                INSERT INTO anime (title, title_en, title_jp, poster, cover, description,
                rating, year, season, status, episodes, duration, studio, external_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (title, title_en, title_jp, poster, cover, description,
                  rating, year, season, status_db, episodes, duration, studio, mal_id))
            db_id = cursor.fetchone()[0]
            
            for genre in anime.get("genres", []):
                gid = genre.get("mal_id")
                if gid and gid in genre_ids:
                    cursor.execute("""
                        INSERT INTO anime_genres (anime_id, genre_id)
                        VALUES (%s, %s) ON CONFLICT DO NOTHING
                    """, (db_id, gid))

            existing_ids.add(mal_id)
            count_added += 1
            print(f"  [{count_added}/50] {title[:40]}", flush=True)
            
            if count_added >= 50:
                break
            time.sleep(1.2)
        
        conn.commit()
        pagination = data.get("pagination", {})
        if not pagination.get("has_next_page"):
            print("  No more pages")
            break
        page += 1
        time.sleep(2)
        
    except Exception as e:
        print(f"  Error: {e}", flush=True)
        time.sleep(10)

cursor.execute("SELECT COUNT(*) FROM anime")
print(f"\nTotal anime: {cursor.fetchone()[0]}")
conn.close()