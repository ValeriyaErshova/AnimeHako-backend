import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.database import SessionLocal, Genre

db = SessionLocal()
try:
    genres = db.query(Genre).all()
    print(f"Genre count: {len(genres)}")
    for g in genres:
        print(f"  {g.id}: {g.name}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
finally:
    db.close()