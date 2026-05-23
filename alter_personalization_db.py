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
    cur.execute("ALTER TABLE briefings ADD COLUMN matched_topics JSONB DEFAULT '[]'::jsonb;")
    cur.execute("ALTER TABLE briefings ADD COLUMN matched_sources JSONB DEFAULT '[]'::jsonb;")
    cur.execute("ALTER TABLE briefings ADD COLUMN personalization_strength FLOAT DEFAULT 0.0;")
    conn.commit()
    print("Database altered successfully with personalization metadata")
except Exception as e:
    print(f"Error altering database: {e}")
cur.close()
conn.close()
