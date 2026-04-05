from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse

from app.database import get_session
from app.models.recalculate_history import RecalculateHistory
from app.schemas.recalculate_history import RecalculateHistoryRead
from app.models.user import User, UserRole
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/search", response_model=list[RecalculateHistoryRead])
async def search_recalculate_history(
    search: Optional[str] = Form(None),
    min_date: Optional[str] = Form(None),
    max_date: Optional[str] = Form(None),
    sort_by: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session)
):
    query = select(RecalculateHistory)

    if search:
        query = query.filter(RecalculateHistory.name.ilike(f"%{search}%"))
    if min_date:
        query = query.filter(RecalculateHistory.recalculated_at >= min_date)
    if max_date:
        query = query.filter(RecalculateHistory.recalculated_at <= max_date)

    if sort_by == "date_asc":
        query = query.order_by(RecalculateHistory.recalculated_at.asc())
    elif sort_by == "date_desc":
        query = query.order_by(RecalculateHistory.recalculated_at.desc())
    elif sort_by == "name_asc":
        query = query.order_by(RecalculateHistory.name.asc())
    elif sort_by == "name_desc":
        query = query.order_by(RecalculateHistory.name.desc())

    result = await session.execute(query)
    return result.scalars().all()


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
