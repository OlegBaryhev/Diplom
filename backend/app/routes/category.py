from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryRead, CategoryBase
from app.models.user import User, UserRole
from app.auth.dependencies import get_current_user
from typing import Optional
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse


router = APIRouter()


@router.post("/search", response_model=list[CategoryRead])
async def search_categories(
    search: Optional[str] = Form(None),
    sort_by: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session)
):
    query = select(Category)
    if search:
        query = query.filter(Category.name.ilike(f"%{search}%"))
    elif sort_by == "name_asc":
        query = query.order_by(Category.name.asc())
    elif sort_by == "name_desc":
        query = query.order_by(Category.name.desc())

    result = await session.execute(query)
    return result.scalars().all()


@router.get("/", response_model=list[CategoryRead])
async def list_categories(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Category))
    return result.scalars().all()


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategoryRead, status_code=201)
async def create_category(category: CategoryCreate, session: AsyncSession = Depends(get_session)):
    new_category = Category(**category.dict())
    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)
    return new_category


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(category_id: int, data: CategoryBase, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.name = data.name
    category.description = data.description
    await session.commit()
    await session.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await session.delete(category)
    await session.commit()
    return None


@router.post("/export/xlsx")
async def export_categories_xlsx(
    search: Optional[str] = Form(None),
    filename: Optional[str] = Form("categories.xlsx"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    query = select(Category)

    if search:
        query = query.filter(Category.name.ilike(f"%{search}%"))

    result = await session.execute(query)
    categories = result.scalars().all()

    data = []
    for category in categories:
        data.append({
            "ID": category.id,
            "Наименование": category.name,
            "Описание": category.description,
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Categories")
    output.seek(0)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
