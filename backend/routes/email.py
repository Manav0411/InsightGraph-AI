from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.services.persistence_service import fetch_briefing_with_articles
from backend.services.email_service import generate_editorial_html
from backend.models.db_user import User

router = APIRouter(prefix="/email", tags=["Email"])

@router.get("/preview/{briefing_id}", response_class=HTMLResponse)
async def preview_email(briefing_id: str, db: Session = Depends(get_db)):
    """
    Renders the Terra-styled email HTML in the browser for development and design iteration.
    """
    briefing = fetch_briefing_with_articles(db, briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")
        
    user = db.query(User).filter(User.id == briefing.user_id).first()
    if not user:
        user = User(id="dummy", email="preview@example.com")
        
    html_content = generate_editorial_html(user, briefing)
    return HTMLResponse(content=html_content)
