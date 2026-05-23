import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.models.logs import LogSettings, UserLog, CategoryLog, BrandLog, OrderLog, ProductLog

LOG_MODELS = {
    "user": UserLog,
    "category": CategoryLog,
    "brand": BrandLog,
    "order": OrderLog,
    "product": ProductLog,
}

async def clean_logs_for_table(session: AsyncSession, table_name: str, model, settings):
    if settings.time_retention_minutes > 0:
        cutoff = datetime.utcnow() - timedelta(minutes=settings.time_retention_minutes)
        await session.execute(
            delete(model).where(model.changed_at < cutoff)
        )
    if settings.count_retention_limit > 0:
        subq = (
            select(model.id)
            .order_by(model.changed_at.desc())
            .limit(settings.count_retention_limit)
            .subquery()
        )
        await session.execute(
            delete(model).where(model.id.not_in(select(subq.c.id)))
        )
    await session.commit()

async def cleanup_all_logs():
    async with SessionLocal() as session:
        settings_result = await session.execute(select(LogSettings))
        all_settings = settings_result.scalars().all()
        for setting in all_settings:
            model = LOG_MODELS.get(setting.table_name)
            if model:
                await clean_logs_for_table(session, setting.table_name, model, setting)

async def start_log_cleanup_scheduler(interval_minutes: int = 5):
    while True:
        await cleanup_all_logs()
        await asyncio.sleep(interval_minutes * 60)