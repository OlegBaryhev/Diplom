from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Optional
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.database import get_session
from app.models.recalculate_history import RecalculateHistory
from app.schemas.recalculate_history import RecalculateHistoryRead
from app.schemas.paginated import PaginatedResponse
from app.models.user import User, UserRole
from app.auth.dependencies import get_current_user

router = APIRouter()

RECALCULATION_TYPE_LABELS = {
    1: "Валютный курс",
    2: "Себестоимость + наценка",
    3: "Скидка по остаткам",
    4: "Цена аналогов",
    5: "Промо-период",
    6: "Накопительная скидка",
    7: "Красивые цены",
    8: "Скидка по рейтингу",
}

TRIGGER_TYPE_LABELS = {
    "manual": "Ручной",
    "schedule": "По расписанию",
    "event": "По событию",
}


class RecalculateHistorySearchRequest(BaseModel):
    search: Optional[str] = None
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    recalculation_type: Optional[int] = None
    trigger_type: Optional[str] = None
    sort_by: Optional[str] = None
    page: int = 1
    page_size: int = 100


@router.post("/search", response_model=PaginatedResponse[RecalculateHistoryRead])
async def search_recalculate_history(
    req: RecalculateHistorySearchRequest,
    session: AsyncSession = Depends(get_session)
):
    conditions = []
    if req.search:
        conditions.append(RecalculateHistory.name.ilike(f"%{req.search}%"))
    if req.min_date:
        conditions.append(RecalculateHistory.recalculated_at >= req.min_date)
    if req.max_date:
        conditions.append(RecalculateHistory.recalculated_at <= req.max_date)
    if req.recalculation_type is not None:
        conditions.append(RecalculateHistory.recalculation_type == req.recalculation_type)
    if req.trigger_type:
        conditions.append(RecalculateHistory.trigger_type == req.trigger_type)

    total = (await session.execute(select(func.count(RecalculateHistory.id)).where(*conditions))).scalar_one()

    query = select(RecalculateHistory).where(*conditions)

    if req.sort_by == "date_asc":
        query = query.order_by(RecalculateHistory.recalculated_at.asc())
    elif req.sort_by == "date_desc":
        query = query.order_by(RecalculateHistory.recalculated_at.desc())
    elif req.sort_by == "name_asc":
        query = query.order_by(RecalculateHistory.name.asc())
    elif req.sort_by == "name_desc":
        query = query.order_by(RecalculateHistory.name.desc())
    else:
        query = query.order_by(RecalculateHistory.recalculated_at.desc())

    query = query.offset((req.page - 1) * req.page_size).limit(req.page_size)
    result = await session.execute(query)
    return {"items": result.scalars().all(), "total": total}


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history_entry(
    history_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")
    result = await session.execute(
        select(RecalculateHistory).where(RecalculateHistory.id == history_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не найдено")
    await session.delete(entry)
    await session.commit()


@router.post("/export/xlsx")
async def export_recalculate_history_xlsx(
    search: Optional[str] = Form(None),
    min_date: Optional[str] = Form(None),
    max_date: Optional[str] = Form(None),
    recalculation_type: Optional[int] = Form(None),
    trigger_type: Optional[str] = Form(None),
    filename: Optional[str] = Form("recalculate_history.xlsx"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")

    query = select(RecalculateHistory)

    if search:
        query = query.filter(RecalculateHistory.name.ilike(f"%{search}%"))
    if min_date:
        query = query.filter(RecalculateHistory.recalculated_at >= min_date)
    if max_date:
        query = query.filter(RecalculateHistory.recalculated_at <= max_date)
    if recalculation_type is not None:
        query = query.filter(RecalculateHistory.recalculation_type == recalculation_type)
    if trigger_type:
        query = query.filter(RecalculateHistory.trigger_type == trigger_type)

    result = await session.execute(query)
    histories = result.scalars().all()

    data = []
    for h in histories:
        data.append({
            "ID": h.id,
            "Наименование": h.name,
            "Описание": h.description or "",
            "Тип перерасчета": RECALCULATION_TYPE_LABELS.get(h.recalculation_type, "") if h.recalculation_type else "",
            "Инициатор": TRIGGER_TYPE_LABELS.get(h.trigger_type, h.trigger_type or ""),
            "Пересчитал": h.recalculated_by,
            "Дата пересчета": h.recalculated_at.strftime("%Y-%m-%d %H:%M:%S") if h.recalculated_at else "",
            "Затронуто товаров": h.products_affected_count or 0,
            "Время выполнения (мс)": h.execution_time_ms or 0,
            "Параметры": str(h.parameters),
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="История перерасчетов")
    output.seek(0)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
