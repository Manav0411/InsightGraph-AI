import json
from dotenv import load_dotenv
load_dotenv()
from backend.db.database import SessionLocal
from backend.services.persistence_service import save_briefing
from backend.schemas.responses import NewsletterResponse

with open("data/runtime/last_newsletter.json") as f:
    data = json.load(f)

response = NewsletterResponse(**data)
db = SessionLocal()
try:
    save_briefing(db, "manav", response)
    print("Success!")
except Exception as e:
    import traceback
    traceback.print_exc()
