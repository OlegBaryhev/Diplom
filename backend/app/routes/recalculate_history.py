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


class RecalculateHistorySearchRequest(BaseModel):
    search: Optional[str] = None
    min_date: Optional[str] = None
    max_date: Optional[str] = None
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

    query = query.offset((req.page - 1) * req.page_size).limit(req.page_size)
    result = await session.execute(query)
    return {"items": result.scalars().all(), "total": total}


@router.post("/export/xlsx")
async def export_recalculate_history_xlsx(
    search: Optional[str] = Form(None),
    min_date: Optional[str] = Form(None),
    max_date: Optional[str] = Form(None),
    filename: Optional[str] = Form("recalculate_history.xlsx"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    query = select(RecalculateHistory)

    if search:
        query = query.filter(RecalculateHistory.name.ilike(f"%{search}%"))
    if min_date:
        query = query.filter(RecalculateHistory.recalculated_at >= min_date)
    if max_date:
        query = query.filter(RecalculateHistory.recalculated_at <= max_date)

    result = await session.execute(query)
    histories = result.scalars().all()

    data = []
    for h in histories:
        data.append({
            "ID": h.id,
            "Наименование": h.name,
            "Описание": h.description,
            "Пересчитал": h.recalculated_by,
            "Дата пересчета": h.recalculated_at.strftime("%Y-%m-%d %H:%M:%S") if h.recalculated_at else "",
            "Параметры": str(h.parameters),
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="RecalculateHistory")
    output.seek(0)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
