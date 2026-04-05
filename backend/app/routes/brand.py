from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.database import get_session
from app.models.brand import Brand
from app.schemas.brand import BrandCreate, BrandRead, BrandBase
from app.models.user import User, UserRole
from app.auth.dependencies import get_current_user
from typing import Optional
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/search", response_model=list[BrandRead])
async def search_brands(
    search: Optional[str] = Form(None),
    sort_by: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session)
):
    query = select(Brand)
    if search:
        query = query.filter(Brand.name.ilike(f"%{search}%"))
    elif sort_by == "name_asc":
        query = query.order_by(Brand.name.asc())
    elif sort_by == "name_desc":
        query = query.order_by(Brand.name.desc())

    result = await session.execute(query)
    return result.scalars().all()

@router.get("/", response_model=list[BrandRead])
async def list_brands(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Brand))
    return result.scalars().all()


@router.get("/{brand_id}", response_model=BrandRead)
async def get_brand(brand_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.post("/", response_model=BrandRead, status_code=201)
async def create_brand(brand: BrandCreate, session: AsyncSession = Depends(get_session)):
    new_brand = Brand(**brand.dict())
    session.add(new_brand)
    await session.commit()
    await session.refresh(new_brand)
    return new_brand


@router.put("/{brand_id}", response_model=BrandRead)
async def update_brand(brand_id: int, data: BrandBase, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    brand.name = data.name
    brand.description = data.description
    await session.commit()
    await session.refresh(brand)
    return brand


@router.delete("/{brand_id}", status_code=204)
async def delete_brand(brand_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    await session.delete(brand)
    await session.commit()
    return None


@router.post("/export/xlsx")
async def export_brands_xlsx(
    search: Optional[str] = Form(None),
    filename: Optional[str] = Form("brands.xlsx"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    query = select(Brand)

    if search:
        query = query.filter(Brand.name.ilike(f"%{search}%"))

    result = await session.execute(query)
    brands = result.scalars().all()

    data = []
    for brand in brands:
        data.append({
            "ID": brand.id,
            "Наименование": brand.name,
            "Описание": brand.description,
            "Зарегистрирован": brand.created_at,
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Brands")
    output.seek(0)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
