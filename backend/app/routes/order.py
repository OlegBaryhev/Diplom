import random, string
from typing import List, Optional
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from io import BytesIO

from fastapi import APIRouter, Depends, Body, HTTPException, Path, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, asc, desc, and_, func
from sqlalchemy.orm import selectinload, joinedload
from app.database import get_session
from app.auth.dependencies import get_current_user
from app.models.order import Order, OrderItem, OrderStatus
from app.schemas.order import OrderRead, OrderCreate
from app.schemas.order_search import OrderSearchRequest

import pandas as pd

from app.schemas.user import UserRead 
from app.models.user import User
from app.models.cart import CartItem

router = APIRouter()

def generate_pickup_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@router.post("/", response_model=OrderRead, status_code=201)
async def create_order(order_data: OrderCreate, session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    pickup_code = generate_pickup_code()
    order = Order(user_id=user.id, pickup_code=pickup_code)
    session.add(order)
    await session.flush()

    for item in order_data.items:
        session.add(OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity))

    await session.commit()
    await session.refresh(order)
    return order

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

@router.patch("/status/{order_id}", response_model=OrderRead)
async def update_order_status(
    order_id: int = Path(..., description="ID заказа"),
    status_update: OrderStatusUpdate = Body(...),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if user.role != "superuser" and order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    order.status = status_update.status
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order

@router.post("/create-by-cart", response_model=OrderRead, status_code=201)
async def create_order_by_cart(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    result = await session.execute(
        select(CartItem).where(CartItem.user_id == user.id)
    )
    cart_items = result.scalars().all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    pickup_code = generate_pickup_code()
    order = Order(user_id=user.id, pickup_code=pickup_code)
    session.add(order)
    await session.flush()

    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        session.add(order_item)

    for cart_item in cart_items:
        await session.delete(cart_item)

    await session.commit()

    result = await session.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order.id)
    )
    order_with_items = result.scalars().first()
    return order_with_items

@router.get("/", response_model=List[OrderRead])
async def get_orders(session: AsyncSession = Depends(get_session), user: User = Depends(get_current_user)):
    result = await session.execute(select(Order).where(Order.user_id == user.id))
    orders = result.scalars().all()
    return orders

class OrderReadExtended(OrderRead):
    total_product_varieties: int
    total_product_quantity: int

@router.post("/search", response_model=List[OrderReadExtended])
async def search_orders(
    req: OrderSearchRequest = Body(...),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    filters = []

    if not (user.role == "superuser"):  
        filters.append(Order.user_id == user.id)
    else:
        if req.user_id is not None:
            filters.append(Order.user_id == req.user_id)

    if req.search:
        subq_user = (
            select(User.id)
            .filter(
                or_(
                    User.name.ilike(f"%{req.search}%"),
                    User.surname.ilike(f"%{req.search}%"),
                )
            )
            .subquery()
        )
        filters.append(
            or_(
                Order.pickup_code.ilike(f"%{req.search}%"),
                Order.user_id.in_(subq_user),
            )
        )

    if req.statuses:
        filters.append(Order.status.in_(req.statuses))

    if req.created_from and req.created_to:
        filters.append(and_(Order.created_at >= req.created_from, Order.created_at <= req.created_to))
    elif req.created_from:
        filters.append(Order.created_at >= req.created_from)
    elif req.created_to:
        filters.append(Order.created_at <= req.created_to)

    if req.quantity_from is not None or req.quantity_to is not None:
        subq_quantity = (
            select(
                OrderItem.order_id,
                func.sum(OrderItem.quantity).label("total_quantity")
            )
            .group_by(OrderItem.order_id)
            .subquery()
        )
        qty_filter = []
        if req.quantity_from is not None:
            qty_filter.append(subq_quantity.c.total_quantity >= req.quantity_from)
        if req.quantity_to is not None:
            qty_filter.append(subq_quantity.c.total_quantity <= req.quantity_to)
        filters.append(
            and_(*qty_filter)
        )
        filters.append(Order.id == subq_quantity.c.order_id)

    query = (
        select(Order)
        .options(
            selectinload(Order.items),
            joinedload(Order.user)
        )
        .where(and_(*filters))
        .order_by(desc(Order.created_at))
    )

    if req.sort_by:
        if req.sort_by == "created_at_asc":
            query = query.order_by(asc(Order.created_at))
        elif req.sort_by == "created_at_desc":
            query = query.order_by(desc(Order.created_at))
        elif req.sort_by == "status_asc":
            query = query.order_by(asc(Order.status))
        elif req.sort_by == "status_desc":
            query = query.order_by(desc(Order.status))

    result = await session.execute(query)
    orders = result.scalars().unique().all()

    response = []
    for order in orders:
        total_varieties = len(order.items)
        total_quantity = sum(item.quantity for item in order.items)
        order_dict = OrderRead.from_orm(order).model_dump()
        order_dict['user'] = order.user
        order_dict['total_product_varieties'] = total_varieties
        order_dict['total_product_quantity'] = total_quantity
        order_data = OrderReadExtended(**order_dict)
        response.append(order_data)

    return response

@router.post("/export/xlsx")
async def export_orders_xlsx(
    search: Optional[str] = Form(None),
    user_id: Optional[int] = Form(None),
    statuses: Optional[List[str]] = Form(None),
    created_from: Optional[str] = Form(None),
    created_to: Optional[str] = Form(None),
    quantity_from: Optional[int] = Form(None),
    quantity_to: Optional[int] = Form(None),
    sort_by: Optional[str] = Form(None),
    filename: Optional[str] = Form("orders.xlsx"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    filters = []

    if not (user.role == "superuser"):
        filters.append(Order.user_id == user.id)
    else:
        if user_id is not None:
            filters.append(Order.user_id == user_id)

    if search:
        subq_user = (
            select(User.id)
            .filter(
                or_(
                    User.name.ilike(f"%{search}%"),
                    User.surname.ilike(f"%{search}%"),
                )
            )
            .subquery()
        )
        filters.append(
            or_(
                Order.pickup_code.ilike(f"%{search}%"),
                Order.user_id.in_(subq_user),
            )
        )

    if statuses:
        filters.append(Order.status.in_(statuses))

    if created_from and created_to:
        filters.append(and_(Order.created_at >= created_from, Order.created_at <= created_to))
    elif created_from:
        filters.append(Order.created_at >= created_from)
    elif created_to:
        filters.append(Order.created_at <= created_to)

    if quantity_from is not None or quantity_to is not None:
        subq_quantity = (
            select(
                OrderItem.order_id,
                func.sum(OrderItem.quantity).label("total_quantity")
            )
            .group_by(OrderItem.order_id)
            .subquery()
        )
        qty_filter = []
        if quantity_from is not None:
            qty_filter.append(subq_quantity.c.total_quantity >= quantity_from)
        if quantity_to is not None:
            qty_filter.append(subq_quantity.c.total_quantity <= quantity_to)
        filters.append(
            and_(*qty_filter)
        )
        filters.append(Order.id == subq_quantity.c.order_id)

    query = (
        select(Order)
        .options(
            selectinload(Order.items),
            joinedload(Order.user)
        )
        .where(and_(*filters))
        .order_by(desc(Order.created_at))
    )

    if sort_by:
        if sort_by == "created_at_asc":
            query = query.order_by(asc(Order.created_at))
        elif sort_by == "created_at_desc":
            query = query.order_by(desc(Order.created_at))
        elif sort_by == "status_asc":
            query = query.order_by(asc(Order.status))
        elif sort_by == "status_desc":
            query = query.order_by(desc(Order.status))

    result = await session.execute(query)
    orders = result.scalars().unique().all()

    data = []
    for order in orders:
        total_varieties = len(order.items)
        total_quantity = sum(item.quantity for item in order.items)
        data.append({
            "ID": order.id,
            "Код доставки": order.pickup_code,
            "Пользователь": f"{order.user.name} {order.user.surname}" if order.user else None,
            "Статус": order.status,
            "Дата создания": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else None,
            "Всего видов товаров": total_varieties,
            "Общее количество товаров": total_quantity,
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Orders")
    output.seek(0)

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )