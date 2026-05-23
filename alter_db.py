import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

url = os.getenv("DATABASE_URL")
if not url:
    print("No DATABASE_URL found")
    exit(1)

conn = psycopg2.connect(url)
cur = conn.cursor()
try:
    cur.execute("ALTER TABLE briefings ADD COLUMN dominant_topics JSONB DEFAULT '[]'::jsonb;")
    cur.execute("ALTER TABLE briefings ADD COLUMN top_signal JSONB;")
    cur.execute("ALTER TABLE briefings ADD COLUMN top_sources JSONB DEFAULT '[]'::jsonb;")
    cur.execute("ALTER TABLE briefings ADD COLUMN signal_quality_index FLOAT DEFAULT 0.0;")
    conn.commit()
    print("Database altered successfully")
except Exception as e:
    print(f"Error altering database: {e}")
cur.close()
conn.close()
