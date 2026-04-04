from dotenv import load_dotenv
load_dotenv()
import os

db_url = os.getenv('DATABASE_URL')
with open('test_output.txt', 'w', encoding='utf-8') as f:
    f.write(f"DATABASE_URL: {repr(db_url)}\n")
    f.write(f"Length: {len(db_url) if db_url else 0}\n")

from app.config import settings
with open('test_output.txt', 'a', encoding='utf-8') as f:
    f.write(f"\nSettings DB URL: {repr(settings.DATABASE_URL)}\n")