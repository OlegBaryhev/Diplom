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
from app.models.products import Product
from app.schemas.products import ProductRead, ProductCreate, ProductBase

router = APIRouter()

@router.post("/export/xlsx")
async def export_products_xlsx(
    search: Optional[str] = Form(None),
    min_price: Optional[int] = Form(None),
    max_price: Optional[int] = Form(None),
    sort_by: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    brand_id: Optional[int] = Form(None),
    filename: Optional[str] = Form("products.xlsx"),
    session: AsyncSession = Depends(get_session),
):
    query = select(Product).options(selectinload(Product.category), selectinload(Product.brand))

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)

    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "name_asc":
        query = query.order_by(Product.name.asc())
    elif sort_by == "name_desc":
        query = query.order_by(Product.name.desc())

    result = await session.execute(query)
    products = result.scalars().all()

    data = []
    for p in products:
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
        df.to_excel(writer, index=False, sheet_name="Products")
    output.seek(0)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )

class ProductSearchRequest(BaseModel):
    search: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    sort_by: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None

@router.post("/search", response_model=list[ProductRead])
async def search_products(
    search_req: ProductSearchRequest,
    session: AsyncSession = Depends(get_session)
):
    query = select(Product).options(selectinload(Product.category), selectinload(Product.brand))

    if search_req.search:
        query = query.filter(Product.name.ilike(f"%{search_req.search}%"))
    if search_req.min_price is not None:
        query = query.filter(Product.price >= search_req.min_price)
    if search_req.max_price is not None:
        query = query.filter(Product.price <= search_req.max_price)
    if search_req.category_id:
        query = query.filter(Product.category_id == search_req.category_id)
    if search_req.brand_id:
        query = query.filter(Product.brand_id == search_req.brand_id)

    if search_req.sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif search_req.sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif search_req.sort_by == "name_asc":
        query = query.order_by(Product.name.asc())
    elif search_req.sort_by == "name_desc":
        query = query.order_by(Product.name.desc())

    result = await session.execute(query)
    products = result.scalars().all()
    return products


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Product).options(selectinload(Product.category), selectinload(Product.brand)).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductRead, status_code=201)
async def create_product(product: ProductCreate, session: AsyncSession = Depends(get_session)):
    new_product = Product(**product.dict())
    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)
    return new_product

@router.put("/{product_id}", response_model=ProductRead)
async def update_product(product_id: int, data: ProductBase, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        product.name = data.name
        product.description = data.description
        product.price = data.price
        product.category_id = data.category_id
        product.brand_id = data.brand_id
        await session.commit()
        await session.refresh(product)
        return product
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await session.delete(product)
    await session.commit()
    return None