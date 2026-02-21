import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.db.database import SessionLocal
from backend.db.models import User

logger = logging.getLogger("uvicorn.error")
scheduler = AsyncIOScheduler()


async def _generate_all_users():
    # Inline import avoids circular dependency at module load time
    from backend.api.recommendations import _generate_for_user

    db = SessionLocal()
    try:
        users = db.query(User).all()
        logger.info(f"Scheduler: generating recommendations for {len(users)} users.")
        for user in users:
            try:
                await _generate_for_user(user.id, db)
                logger.info(f"Scheduler: generated recs for user {user.id}.")
            except Exception as exc:
                logger.error(f"Scheduler: failed for user {user.id}: {exc}")
    finally:
        db.close()


def start_scheduler():
    # day_of_week=6 = Sunday in APScheduler (0 = Monday)
    scheduler.add_job(
        _generate_all_users,
        "cron",
        day_of_week=6,
        hour=18,
        minute=0,
        id="weekly_recs",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started — weekly recs will run Sundays at 18:00.")


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped.")
