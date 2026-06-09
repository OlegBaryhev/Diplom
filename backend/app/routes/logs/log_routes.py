from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_, or_, Text
from sqlalchemy.sql import asc, desc
from typing import Optional, List
from app.database import get_session
from app.models.logs import (
    UserLog, CategoryLog, BrandLog, OrderLog, ProductLog, LogSettings
)
from app.schemas.logs import LogEntryBase, LogFilter, LogSettingsBase, LogSettingsUpdate
from app.auth.dependencies import get_current_user, has_permission
from app.models.user import User

router = APIRouter(tags=["Logs"])

LOG_MODELS = {
    "user": UserLog,
    "category": CategoryLog,
    "brand": BrandLog,
    "order": OrderLog,
    "product": ProductLog,
}

async def get_log_model(table_name: str):
    model = LOG_MODELS.get(table_name)
    if not model:
        raise HTTPException(status_code=404, detail="Invalid log table name")
    return model

@router.post("/{table_name}/search", response_model=List[LogEntryBase])
async def search_logs(
    table_name: str,
    filters: LogFilter,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(has_permission("logs", "read"))
):
    model = await get_log_model(table_name)
    query = select(model)

    conditions = []
    if filters.search:
        conditions.append(model.row_data.cast(Text).ilike(f"%{filters.search}%"))
    if filters.operation:
        conditions.append(model.operation == filters.operation)
    if filters.date_from:
        conditions.append(model.changed_at >= filters.date_from)
    if filters.date_to:
        conditions.append(model.changed_at <= filters.date_to)
    if conditions:
        query = query.where(and_(*conditions))

    if filters.sort_by == "changed_at_asc":
        query = query.order_by(asc(model.changed_at))
    elif filters.sort_by == "changed_at_desc":
        query = query.order_by(desc(model.changed_at))
    elif filters.sort_by == "operation_asc":
        query = query.order_by(asc(model.operation))
    elif filters.sort_by == "operation_desc":
        query = query.order_by(desc(model.operation))
    else:
        query = query.order_by(desc(model.changed_at))

    result = await session.execute(query)
    logs = result.scalars().all()
    return logs

@router.delete("/{table_name}/truncate", status_code=204)
async def truncate_log_table(
    table_name: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(has_permission("logs", "delete"))
):
    model = await get_log_model(table_name)
    await session.execute(delete(model))
    await session.commit()

@router.delete("/{table_name}/{log_id}", status_code=204)
async def delete_log_entry(
    table_name: str,
    log_id: int = Path(..., gt=0),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(has_permission("logs", "delete"))
):
    model = await get_log_model(table_name)
    result = await session.execute(select(model).where(model.id == log_id))
    log_entry = result.scalar_one_or_none()
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
    await session.delete(log_entry)
    await session.commit()

@router.get("/settings", response_model=List[LogSettingsBase])
async def get_all_log_settings(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(has_permission("logs", "read"))
):
    result = await session.execute(select(LogSettings))
    return result.scalars().all()

@router.get("/settings/{table_name}", response_model=LogSettingsBase)
async def get_log_settings(
    table_name: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(has_permission("logs", "read"))
):
    result = await session.execute(select(LogSettings).where(LogSettings.table_name == table_name))
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=404, detail="Settings not found")
    return setting

@router.put("/settings/{table_name}", response_model=LogSettingsBase)
async def update_log_settings(
    table_name: str,
    update: LogSettingsUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(has_permission("logs", "edit"))
):
    result = await session.execute(select(LogSettings).where(LogSettings.table_name == table_name))
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=404, detail="Settings not found")
    if update.time_retention_minutes is not None:
        setting.time_retention_minutes = update.time_retention_minutes
    if update.count_retention_limit is not None:
        setting.count_retention_limit = update.count_retention_limit
    await session.commit()
    await session.refresh(setting)
    return setting