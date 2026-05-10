from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.database import get_session
from app.models.products import Product
from app.models.recalculate_history import RecalculateHistory
from app.schemas.recalculate_history import (
    RelativePriceUpdateRequest,
    FixedPriceUpdateRequest,
    AverageRelativePriceUpdateRequest,
    PriceRecalculationFilter,
)
from app.schemas.products import ProductRead
from app.models.user import User 
from app.auth.dependencies import get_current_user

router = APIRouter()

async def apply_filters_products(session: AsyncSession, filters: PriceRecalculationFilter) -> List[Product]:
    query = select(Product)
    if filters.search:
        query = query.filter(Product.name.ilike(f"%{filters.search}%"))
    if filters.min_price is not None:
        query = query.filter(Product.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.filter(Product.price <= filters.max_price)
    if filters.category_id:
        query = query.filter(Product.category_id == filters.category_id)
    if filters.brand_id:
        query = query.filter(Product.brand_id == filters.brand_id)
    if filters.sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif filters.sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif filters.sort_by == "name_asc":
        query = query.order_by(Product.name.asc())
    elif filters.sort_by == "name_desc":
        query = query.order_by(Product.name.desc())

    result = await session.execute(query)
    return result.scalars().all()


@router.post("/relative_current_price", response_model=List[ProductRead])
async def recalculate_relative_current_price(
    req: RelativePriceUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    products = await apply_filters_products(session, req)

    for p in products:
        if req.type == "rubles":
            new_price = p.price + req.value
        else:
            new_price = p.price * (1 + req.value / 100)
        p.price = max(0, int(round(new_price)))

    await session.commit()

    history = RecalculateHistory(
        name=req.name,
        description=req.description,
        recalculated_by=current_user.username,
        parameters=req.dict(exclude={"recalculated_by"}),
    )
    session.add(history)
    await session.commit()

    return products


@router.post("/fixed_value", response_model=List[ProductRead])
async def recalculate_fixed_value(
    req: FixedPriceUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    products = await apply_filters_products(session, req)

    for p in products:
        p.price = max(0, req.value)

    await session.commit()

    history = RecalculateHistory(
        name=req.name,
        description=req.description,
        recalculated_by=current_user.username,
        parameters=req.dict(exclude={"recalculated_by"}),
    )
    session.add(history)
    await session.commit()

    return products


@router.post("/average_relative_price", response_model=List[ProductRead])
async def recalculate_average_relative_price(
    req: AverageRelativePriceUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    products = await apply_filters_products(session, req)

    analog_filters = PriceRecalculationFilter(
        search=req.search,
        min_price=req.min_price,
        max_price=req.max_price,
        sort_by=None,
        category_id=req.category_id,
        brand_id=req.brand_id,
    )
    analogs = await apply_filters_products(session, analog_filters)

    avg_analogs_price = (
        sum(a.price for a in analogs) / len(analogs) if analogs else 0
    )
    avg_products_price = (
        sum(p.price for p in products) / len(products) if products else 0
    )
    avg_total_price = (avg_analogs_price + avg_products_price) / 2

    for p in products:
        if req.type == "rubles":
            val = req.value
        else:
            val = avg_total_price * (req.value / 100)

        if req.offset:
            p.price = max(
                0, int(round(avg_total_price + (p.price - avg_total_price) + val))
            )
        else:
            p.price = max(0, int(round(p.price + val)))

    await session.commit()

    history = RecalculateHistory(
        name=req.name,
        description=req.description,
        recalculated_by=current_user.username,
        parameters=req.dict(exclude={"recalculated_by"}),
    )
    session.add(history)
    await session.commit()

    return products
