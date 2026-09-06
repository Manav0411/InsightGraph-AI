import os
import resend
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.db_user import User
from backend.models.db_briefing import Briefing
from backend.models.db_email_log import EmailDeliveryLog
from utils.logger import get_logger

logger = get_logger("email_service")

resend.api_key = os.environ.get("RESEND_API_KEY", "")

FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://www.insightgraph.dev").rstrip("/")


def send_admin_alert(subject: str, body: str) -> None:
    """
    Fire-and-forget operational alert to every address in ADMIN_EMAILS.
    Never raises - alerting must not break the caller.
    """
    admins = [e.strip() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()]
    if not admins or not os.environ.get("RESEND_API_KEY"):
        logger.warning(f"[alert] {subject} (no ADMIN_EMAILS / RESEND_API_KEY configured)")
        return
    try:
        resend.Emails.send({
            "from": "InsightGraph Ops <intelligence@insightgraph.dev>",
            "to": admins,
            "subject": f"[InsightGraph] {subject}",
            "text": body,
        })
        logger.info(f"[alert] Sent admin alert: {subject}")
    except Exception as e:
        logger.error(f"[alert] Failed to send admin alert '{subject}': {e}")


def render_header(briefing: Briefing) -> str:
    date_str = briefing.generated_at.strftime("%B %d, %Y")
    sqi = round(briefing.signal_quality_index, 1)
    topics = ", ".join(briefing.dominant_topics[:3]) if briefing.dominant_topics else "Ecosystem Shift"
    
    return f"""
    <div style="margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid #E5E7EB;">
        <h1 style="margin: 0; font-size: 24px; font-weight: 700; color: #111827; letter-spacing: -0.5px;">InsightGraph</h1>
        <p style="margin: 4px 0 0; font-size: 14px; color: #6B7280; text-transform: uppercase; letter-spacing: 1px;">Daily Intelligence Ritual</p>
        
        <div style="margin-top: 24px; background-color: #F9FAFB; padding: 16px; border-radius: 8px;">
            <div style="font-size: 13px; color: #4B5563; margin-bottom: 8px;">
                <strong>Date:</strong> {date_str} &nbsp;|&nbsp; <strong>SQI:</strong> <span style="color: #059669; font-weight: 600;">{sqi}</span>
            </div>
            <div style="font-size: 13px; color: #4B5563;">
                <strong>Dominant Topics:</strong> {topics}
            </div>
        </div>
    </div>
    """

def render_signal_card(article) -> str:
    score = round(article.trend_score, 1)
    return f"""
    <div style="margin-bottom: 24px;">
        <h3 style="margin: 0 0 8px; font-size: 18px; font-weight: 600; color: #111827;">
            <a href="{article.url}" style="color: #2563EB; text-decoration: none;">{article.title}</a>
        </h3>
        <div style="font-size: 12px; color: #6B7280; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
            {article.source} &nbsp;|&nbsp; Trend Score: {score}
        </div>
        <p style="margin: 0 0 12px; font-size: 15px; line-height: 1.6; color: #374151;">
            {article.summary}
        </p>
        <div style="background-color: #EFF6FF; border-left: 4px solid #3B82F6; padding: 12px 16px; margin: 0;">
            <p style="margin: 0; font-size: 14px; line-height: 1.5; color: #1E3A8A;">
                <strong>Why It Matters:</strong> {article.why_it_matters}
            </p>
        </div>
    </div>
    """

def render_personalized_signals(briefing: Briefing) -> str:
    if not briefing.matched_topics and not briefing.matched_sources:
        return ""
    
    reasons = []
    if briefing.matched_topics:
        reasons.append(f"topics: {', '.join(briefing.matched_topics)}")
    if briefing.matched_sources:
        reasons.append(f"trusted sources: {', '.join(briefing.matched_sources)}")
        
    return f"""
    <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid #E5E7EB;">
        <h2 style="margin: 0 0 16px; font-size: 14px; font-weight: 700; color: #9CA3AF; text-transform: uppercase; letter-spacing: 1px;">Personalized For You</h2>
        <p style="margin: 0; font-size: 14px; color: #4B5563;">
            Signals in this briefing were elevated due to alignment with your preferred {"; ".join(reasons)}.
        </p>
    </div>
    """

def render_footer(briefing: Briefing) -> str:
    reliability = round(briefing.grounding_reliability, 1)
    val_success = round(briefing.validation_success_rate, 1)
    return f"""
    <div style="margin-top: 48px; padding-top: 32px; border-top: 1px solid #E5E7EB; text-align: center;">
        <a href="{FRONTEND_URL}/" style="display: inline-block; background-color: #111827; color: #FFFFFF; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-size: 14px; font-weight: 600; margin-bottom: 24px;">
            Open Observatory
        </a>
        
        <div style="font-size: 12px; color: #9CA3AF; margin-bottom: 8px;">
            Grounding Reliability: {reliability}% &nbsp;|&nbsp; Validation Success: {val_success}%
        </div>
        <p style="margin: 0; font-size: 12px; color: #9CA3AF; font-style: italic;">
            Autonomously synthesized from today's AI ecosystem signals.
        </p>
    </div>
    """

def generate_editorial_html(user: User, briefing: Briefing) -> str:
    html_parts = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'></head>",
        "<body style='margin: 0; padding: 0; background-color: #FFFFFF; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif;'>",
        "<div style='max-width: 600px; margin: 0 auto; padding: 32px 20px;'>",
        render_header(briefing)
    ]
    
    html_parts.append("<div style='margin-bottom: 32px;'>")
    html_parts.append("<h2 style='margin: 0 0 24px; font-size: 14px; font-weight: 700; color: #9CA3AF; text-transform: uppercase; letter-spacing: 1px;'>Top Intelligence Signals</h2>")
    for article in briefing.articles:
        html_parts.append(render_signal_card(article))
    html_parts.append("</div>")
    
    html_parts.append(render_personalized_signals(briefing))
    html_parts.append(render_footer(briefing))
    
    html_parts.append("</div></body></html>")
    return "\n".join(html_parts)

def generate_plaintext(user: User, briefing: Briefing) -> str:
    date_str = briefing.generated_at.strftime("%B %d, %Y")
    sqi = round(briefing.signal_quality_index, 1)
    
    lines = [
        "InsightGraph - Daily Intelligence Ritual",
        f"Date: {date_str} | SQI: {sqi}",
        "---",
        "Top Intelligence Signals:"
    ]
    
    for article in briefing.articles:
        lines.append(f"\\n* {article.title}")
        lines.append(f"  Source: {article.source} | Trend: {round(article.trend_score, 1)}")
        lines.append(f"  {article.summary}")
        lines.append(f"  Why It Matters: {article.why_it_matters}")
        lines.append(f"  Link: {article.url}")
        
    lines.append("\\n---")
    lines.append(f"Grounding Reliability: {round(briefing.grounding_reliability, 1)}% | Validation Success: {round(briefing.validation_success_rate, 1)}%")
    lines.append("Autonomously synthesized from today's AI ecosystem signals.")
    
    return "\n".join(lines)


async def send_briefing_email(db: Session, user: User, briefing: Briefing):
    """
    Constructs the editorial email and sends it via Resend with a strict timeout.
    Persists delivery telemetry.
    """
    logger.info(f"[email] Preparing email delivery for user {user.id}, briefing {briefing.id}")
    
    html_content = generate_editorial_html(user, briefing)
    text_content = generate_plaintext(user, briefing)
    
    recipient_email = user.email if user.email else "user@example.com"
    
    delivery_log = EmailDeliveryLog(
        user_id=user.id,
        briefing_id=briefing.id,
        recipient_email=recipient_email,
        rendered_email_html=html_content,
        template_version="v1.0.0",
        delivery_type="daily_digest"
    )
    db.add(delivery_log)
    
    if not os.environ.get("RESEND_API_KEY"):
        logger.warning(f"[email] RESEND_API_KEY not set. Skipping actual delivery for {recipient_email}")
        delivery_log.status = "skipped_no_api_key"
        db.commit()
        return

    params = {
        "from": "InsightGraph <intelligence@insightgraph.dev>",
        "to": recipient_email,
        "subject": f"InsightGraph Daily Briefing - SQI {round(briefing.signal_quality_index, 1)}",
        "html": html_content,
        "text": text_content
    }

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(resend.Emails.send, params), 
            timeout=10.0
        )
        logger.info(f"[email] Successfully delivered briefing to {recipient_email}")
        delivery_log.status = "success"
        delivery_log.provider_message_id = response.get("id") if isinstance(response, dict) else None
    except asyncio.TimeoutError:
        logger.error(f"[email] ERROR: Delivery to {recipient_email} timed out after 10s")
        delivery_log.status = "failed"
        delivery_log.error_message = "Timeout error"
    except Exception as e:
        logger.error(f"[email] ERROR: Failed to deliver briefing email for user {user.id}: {str(e)}")
        delivery_log.status = "failed"
        delivery_log.error_message = str(e)
    finally:
        db.commit()
