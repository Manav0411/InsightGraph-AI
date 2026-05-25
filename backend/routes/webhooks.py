import os
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from svix.webhooks import Webhook, WebhookVerificationError
from backend.db.database import get_db
from backend.services.persistence_service import create_or_get_user
from utils.logger import get_logger

logger = get_logger("webhooks")
router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/clerk")
async def clerk_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook endpoint to receive events from Clerk.
    Powered by Svix signature verification.
    """
    secret = os.environ.get("CLERK_WEBHOOK_SECRET")
    if not secret:
        logger.error("CLERK_WEBHOOK_SECRET is not configured.")
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    payload = await request.body()
    headers = request.headers

    # Extract Svix headers
    svix_id = headers.get("svix-id")
    svix_timestamp = headers.get("svix-timestamp")
    svix_signature = headers.get("svix-signature")

    if not svix_id or not svix_timestamp or not svix_signature:
        logger.error("Missing Svix headers in webhook payload")
        raise HTTPException(status_code=400, detail="Missing Svix headers")

    wh = Webhook(secret)
    try:
        # svix expects payload as bytes or string. Request.body() is bytes.
        event = wh.verify(payload, headers)
    except WebhookVerificationError as e:
        logger.error(f"Webhook verification failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event.get("type")
    data = event.get("data", {})

    logger.info(f"Received Clerk Webhook: {event_type}")

    if event_type == "user.created":
        user_id = data.get("id")
        email_addresses = data.get("email_addresses", [])
        email = None
        if email_addresses and len(email_addresses) > 0:
            email = email_addresses[0].get("email_address")
            
        if user_id:
            logger.info(f"Syncing new Clerk user {user_id} to database...")
            create_or_get_user(db, user_id, email=email)
        else:
            logger.warning("Received user.created event without user ID.")

    return {"status": "success", "message": "Webhook processed"}
