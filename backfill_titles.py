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
    cur.execute("SELECT id, dominant_topics FROM briefings;")
    rows = cur.fetchall()
    
    for row in rows:
        briefing_id = row[0]
        topics = row[1]
        
        if topics and len(topics) > 0:
            top_two = topics[:2]
            title_suffix = " & ".join(top_two)
            new_title = f"InsightGraph Digest: {title_suffix}"
        else:
            new_title = "InsightGraph Digest"
            
        cur.execute("UPDATE briefings SET title = %s WHERE id = %s", (new_title, briefing_id))
        
    conn.commit()
    print(f"Updated {len(rows)} briefings with dynamic titles successfully.")
except Exception as e:
    print(f"Error updating database: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()
