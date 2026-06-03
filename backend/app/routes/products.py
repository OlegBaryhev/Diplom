from typing import Optional
from io import BytesIO
import os
import uuid
import shutil

from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, text

import pandas as pd

from app.database import get_session
from app.models.products import Product
from app.models.product_image import ProductImage
from app.schemas.products import ProductRead, ProductCreate, ProductBase
from app.schemas.paginated import PaginatedResponse

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGES_PER_PRODUCT = 10
PRODUCT_IMAGES_DIR = "product_images"
os.makedirs(PRODUCT_IMAGES_DIR, exist_ok=True)


def _load_opts():
    return [
        selectinload(Product.category),
        selectinload(Product.brand),
        selectinload(Product.images),
    ]

@router.post("/{product_id}/images", response_model=ProductRead)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    is_primary: bool = Form(False),
    session: AsyncSession = Depends(get_session),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Недопустимый тип файла. Разрешены: JPEG, PNG, WebP, GIF",
        )

    result = await session.execute(
        select(Product).options(*_load_opts()).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if len(product.images) >= MAX_IMAGES_PER_PRODUCT:
        raise HTTPException(
            status_code=400,
            detail=f"Максимум {MAX_IMAGES_PER_PRODUCT} изображений на один продукт",
        )

    ext = os.path.splitext(file.filename or "")[-1].lower() or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(PRODUCT_IMAGES_DIR, filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    make_primary = is_primary or not product.images
    if make_primary:
        for img in product.images:
            img.is_primary = False

    order_value = max((img.order for img in product.images), default=-1) + 1
    image = ProductImage(
        product_id=product_id,
        url=f"/product_images/{filename}",
        is_primary=make_primary,
        order=order_value,
    )
    session.add(image)
    await session.commit()

    result = await session.execute(
        select(Product).options(*_load_opts()).where(Product.id == product_id)
    )
    return result.scalar_one()


@router.delete("/{product_id}/images/{image_id}", status_code=204)
async def delete_product_image(
    product_id: int,
    image_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(ProductImage).where(
            ProductImage.id == image_id,
            ProductImage.product_id == product_id,
        )
    )
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = image.url.lstrip("/")
    if os.path.exists(file_path):
        os.remove(file_path)

    was_primary = image.is_primary
    await session.delete(image)
    await session.flush()

    if was_primary:
        remaining = await session.execute(
            select(ProductImage)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.order)
            .limit(1)
        )
        first = remaining.scalar_one_or_none()
        if first:
            first.is_primary = True

    await session.commit()
    return None


@router.put("/{product_id}/images/{image_id}/set-primary", response_model=ProductRead)
async def set_primary_image(
    product_id: int,
    image_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Product).options(*_load_opts()).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not any(img.id == image_id for img in product.images):
        raise HTTPException(status_code=404, detail="Image not found")

    for img in product.images:
        img.is_primary = img.id == image_id

    await session.commit()
    result = await session.execute(
        select(Product).options(*_load_opts()).where(Product.id == product_id)
    )
    return result.scalar_one()

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
        discounted = round(p.price * (1 - p.discount / 100)) if p.discount else p.price
        data.append({
            "ID": p.id,
            "Наименование": p.name,
            "Описание": p.description,
            "Цена": p.price,
            "Скидка, %": p.discount,
            "Цена со скидкой": discounted,
            "Категория": p.category.name if p.category else None,
            "Бренд": p.brand.name if p.brand else None,
        })
    df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Products")
    output.seek(0)

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
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
    page: int = 1
    page_size: int = 100


@router.post("/search", response_model=PaginatedResponse[ProductRead])
async def search_products(
    search_req: ProductSearchRequest,
    session: AsyncSession = Depends(get_session),
):
    conditions = []
    if search_req.search:
        conditions.append(Product.name.ilike(f"%{search_req.search}%"))
    if search_req.min_price is not None:
        conditions.append(Product.price >= search_req.min_price)
    if search_req.max_price is not None:
        conditions.append(Product.price <= search_req.max_price)
    if search_req.category_id:
        conditions.append(Product.category_id == search_req.category_id)
    if search_req.brand_id:
        conditions.append(Product.brand_id == search_req.brand_id)

    total = (
        await session.execute(select(func.count(Product.id)).where(*conditions))
    ).scalar_one()

    query = select(Product).options(*_load_opts()).where(*conditions)

    if search_req.sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif search_req.sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif search_req.sort_by == "name_asc":
        query = query.order_by(Product.name.asc())
    elif search_req.sort_by == "name_desc":
        query = query.order_by(Product.name.desc())

    query = query.offset((search_req.page - 1) * search_req.page_size).limit(search_req.page_size)
    result = await session.execute(query)
    return {"items": result.scalars().all(), "total": total}

@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Product).options(*_load_opts()).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductRead, status_code=201)
async def create_product(product: ProductCreate, session: AsyncSession = Depends(get_session)):
    new_product = Product(**product.model_dump())
    session.add(new_product)
    await session.commit()

    result = await session.execute(
        select(Product).options(*_load_opts()).where(Product.id == new_product.id)
    )
    return result.scalar_one()


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    data: ProductBase,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        product.name = data.name
        product.description = data.description
        product.price = data.price
        product.discount = data.discount
        product.category_id = data.category_id
        product.brand_id = data.brand_id
        await session.commit()

        result = await session.execute(
            select(Product).options(*_load_opts()).where(Product.id == product_id)
        )
        return result.scalar_one()
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
