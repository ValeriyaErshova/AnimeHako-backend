import requests
import psycopg2
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {'X-Application': 'pvn098-w3n50vndg'}
DSN = 'postgresql://postgres:123456@localhost:5432/animehako'

conn = psycopg2.connect(DSN)
cursor = conn.cursor()

cursor.execute('TRUNCATE screenshots, anime RESTART IDENTITY CASCADE')
conn.commit()
print('Cleared tables')

all_anime = []
page = 1

while len(all_anime) < 100:
    response = requests.get(f'https://api.yani.tv/anime?page={page}', headers=headers)
    if response.status_code != 200:
        print(f'Error on page {page}: {response.status_code}')
        break
    data = response.json()
    items = data.get('response', [])
    if not items:
        break
    all_anime.extend(items)
    print(f'Page {page}: got {len(items)} anime, total: {len(all_anime)}')
    page += 1
    time.sleep(0.5)

print(f'Total anime fetched: {len(all_anime)}')

saved = 0
for anime in all_anime[:100]:
    try:
        title = anime.get('title', 'Unknown')
        description = anime.get('description', '')
        year = anime.get('year')
        poster = 'https:' + anime.get('poster', {}).get('huge', '') if anime.get('poster') else None
        rating = anime.get('rating', {}).get('average')

        cursor.execute('''
            INSERT INTO anime (title, description, year, poster, rating, external_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (title, description, year, poster, rating, str(anime.get('anime_id', ''))))

        db_id = cursor.fetchone()[0]
        saved += 1
        print(f'[{saved}] {title}')
    except Exception as e:
        print(f'Error saving {title}: {e}')

    time.sleep(0.3)

conn.commit()
cursor.execute('SELECT COUNT(*) FROM anime')
print(f'Total anime in DB: {cursor.fetchone()[0]}')
cursor.close()
conn.close()