from typing import Optional
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

import pandas as pd

from app.database import get_session
from app.models.analogs import Analog
from app.schemas.analogs import AnalogRead, AnalogCreate, AnalogBase

router = APIRouter()

@router.post("/export/xlsx")
async def export_analogs_xlsx(
    search: Optional[str] = Form(None),
    min_price: Optional[int] = Form(None),
    max_price: Optional[int] = Form(None),
    sort_by: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    brand_id: Optional[int] = Form(None),
    filename: Optional[str] = Form("analogs.xlsx"),
    session: AsyncSession = Depends(get_session),
):
    query = select(Analog).options(selectinload(Analog.category), selectinload(Analog.brand))

    if search:
        query = query.filter(Analog.name.ilike(f"%{search}%"))
    if min_price is not None:
        query = query.filter(Analog.price >= min_price)
    if max_price is not None:
        query = query.filter(Analog.price <= max_price)
    if category_id:
        query = query.filter(Analog.category_id == category_id)
    if brand_id:
        query = query.filter(Analog.brand_id == brand_id)

    if sort_by == "price_asc":
        query = query.order_by(Analog.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Analog.price.desc())
    elif sort_by == "name_asc":
        query = query.order_by(Analog.name.asc())
    elif sort_by == "name_desc":
        query = query.order_by(Analog.name.desc())

    result = await session.execute(query)
    analogs = result.scalars().all()

    data = []
    for p in analogs:
        data.append({
            "ID": p.id,
            "Наименование": p.name,
            "Описание": p.description,
            "Цена": p.price,
            "Категория": p.category.name if p.category else None,
            "Бренд": p.brand.name if p.brand else None,
        })
    df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Analogs")
    output.seek(0)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )

class AnalogSearchRequest(BaseModel):
    search: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    sort_by: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None

@router.post("/search", response_model=list[AnalogRead])
async def search_analogs(
    search_req: AnalogSearchRequest,
    session: AsyncSession = Depends(get_session)
):
    query = select(Analog).options(selectinload(Analog.category), selectinload(Analog.brand))

    if search_req.search:
        query = query.filter(Analog.name.ilike(f"%{search_req.search}%"))
    if search_req.min_price is not None:
        query = query.filter(Analog.price >= search_req.min_price)
    if search_req.max_price is not None:
        query = query.filter(Analog.price <= search_req.max_price)
    if search_req.category_id:
        query = query.filter(Analog.category_id == search_req.category_id)
    if search_req.brand_id:
        query = query.filter(Analog.brand_id == search_req.brand_id)

    if search_req.sort_by == "price_asc":
        query = query.order_by(Analog.price.asc())
    elif search_req.sort_by == "price_desc":
        query = query.order_by(Analog.price.desc())
    elif search_req.sort_by == "name_asc":
        query = query.order_by(Analog.name.asc())
    elif search_req.sort_by == "name_desc":
        query = query.order_by(Analog.name.desc())

    result = await session.execute(query)
    analogs = result.scalars().all()
    return analogs


@router.get("/{analog_id}", response_model=AnalogRead)
async def get_analog(analog_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Analog).options(selectinload(Analog.category), selectinload(Analog.brand)).where(Analog.id == analog_id))
    analog = result.scalar_one_or_none()
    if not analog:
        raise HTTPException(status_code=404, detail="Analog not found")
    return analog