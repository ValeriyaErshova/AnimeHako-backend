from sqlalchemy import create_engine, text
from app.config import settings
import traceback

try:
    engine = create_engine(settings.DATABASE_URL)
    with open('engine_test.txt', 'w', encoding='utf-8') as f:
        f.write("Engine created successfully\n")
    
    with engine.connect() as conn:
        with open('engine_test.txt', 'a', encoding='utf-8') as f:
            f.write("Connected successfully\n")
        
        result = conn.execute(text('SELECT id, name FROM genres'))
        with open('engine_test.txt', 'a', encoding='utf-8') as f:
            f.write(f"Query executed, rows: {result.rowcount}\n")
            for row in result:
                f.write(f"  {row[0]}: {row[1]}\n")
except Exception as e:
    with open('engine_test.txt', 'w', encoding='utf-8') as f:
        f.write(f"Error: {type(e).__name__}: {e}\n")
        traceback.print_exc(file=f)