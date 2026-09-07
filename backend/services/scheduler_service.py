from backend.services.workflow_service import generate_autonomous_briefing
from backend.db.database import SessionLocal
from backend.models.db_user import User
from utils.logger import get_logger

logger = get_logger("scheduler")


async def daily_intelligence_generation() -> dict:
    """
    Orchestrates intelligence generation for every email-enabled user.
    Returns a run summary and emails the admins if anything failed.

    Triggered externally via POST /scheduler/run-now (GitHub Actions cron).
    """
    logger.info("[scheduler] Starting scheduled daily intelligence generation.")

    user_ids_to_process = []
    with SessionLocal() as db:
        users = db.query(User).all()
        for u in users:
            # Default to True if preferences are missing
            if not u.preferences or getattr(u.preferences, 'email_delivery_enabled', True):
                user_ids_to_process.append(u.id)

    if not user_ids_to_process:
        logger.warning("[scheduler] No users found with email delivery enabled for daily generation.")
        return {"processed": 0, "succeeded": 0, "failed": 0, "failures": []}

    succeeded = 0
    failures = []
    for user_id in user_ids_to_process:
        try:
            await generate_autonomous_briefing(user_id)
            succeeded += 1
        except Exception as e:
            logger.error(f"[scheduler] Failed autonomous generation for user {user_id}: {e}")
            failures.append({"user_id": user_id, "error": str(e)})

    summary = {
        "processed": len(user_ids_to_process),
        "succeeded": succeeded,
        "failed": len(failures),
        "failures": failures,
    }
    logger.info(f"[scheduler] Completed daily generation: {summary['succeeded']}/{summary['processed']} succeeded.")

    if failures:
        try:
            from backend.services.email_service import send_admin_alert
            lines = [f"- {f['user_id']}: {f['error']}" for f in failures]
            send_admin_alert(
                subject=f"Daily briefing: {len(failures)}/{summary['processed']} user(s) failed",
                body=(
                    f"Succeeded: {succeeded}\nFailed: {len(failures)}\n\n"
                    + "\n".join(lines)
                ),
            )
        except Exception as e:
            logger.error(f"[scheduler] Could not send failure alert: {e}")

    return summary
