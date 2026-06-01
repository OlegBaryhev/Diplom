from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, asc, desc
from app.database import get_session
from app.models.cart import CartItem
from app.models.products import Product
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.cart import CartItemRead, CartItemCreate, CartSearchRequest, CartSummary, CartItemUpdate
from app.schemas.paginated import PaginatedResponse
from app.schemas.user import UserRead
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from app.schemas.products import ProductRead

router = APIRouter()

@router.post("/search", response_model=PaginatedResponse[CartSummary])
async def search_carts(
    req: CartSearchRequest = Body(...),
    session: AsyncSession = Depends(get_session),
):
    subq_user = select(User.id).filter(
        or_(
            User.name.ilike(f"%{req.search}%" if req.search else "%%"),
            User.surname.ilike(f"%{req.search}%" if req.search else "%%"),
            User.email.ilike(f"%{req.search}%" if req.search else "%%"),
        )
    ).subquery()

    query = (
        select(User, CartItem, Product)
        .join(CartItem, CartItem.user_id == User.id)
        .join(Product, Product.id == CartItem.product_id)
        .filter(User.id.in_(subq_user))
    )

    if req.sort_by == "name_asc":
        query = query.order_by(
            asc(User.name), asc(User.surname), asc(CartItem.id)
        )
    elif req.sort_by == "name_desc":
        query = query.order_by(
            desc(User.name), desc(User.surname), desc(CartItem.id)
        )

    result = await session.execute(query)
    rows = result.all()

    user_aggregate = {}
    for user, cart_item, product in rows:
        if user.id not in user_aggregate:
            user_aggregate[user.id] = {
                "id": cart_item.id,
                "user": user,
                "products_total": 0,
                "total_price": 0,
            }
        user_aggregate[user.id]["products_total"] += cart_item.quantity
        user_aggregate[user.id]["total_price"] += product.price * cart_item.quantity

    total = len(user_aggregate)
    start = (req.page - 1) * req.page_size
    end = start + req.page_size
    paginated_values = list(user_aggregate.values())[start:end]

    response = []
    for data in paginated_values:
        response.append(
            CartSummary(
                id=data["id"],
                user=UserRead.from_orm(data["user"]),
                products_total=data["products_total"],
                total_price=data["total_price"],
            )
        )

    return {"items": response, "total": total}


@router.get("/", response_model=list[CartItemRead])
async def get_cart(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    result = await session.execute(
        select(CartItem)
        .options(
            selectinload(CartItem.product)
            .selectinload(Product.category),
            selectinload(CartItem.product)
            .selectinload(Product.brand),
        )
        .where(CartItem.user_id == current_user.id)
    )
    cart_items = result.scalars().all()
    return cart_items


@router.post("/", response_model=CartItemRead, status_code=201)
async def add_to_cart(
    item: CartItemCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    product_result = await session.execute(
        select(Product).where(Product.id == item.product_id)
    )
    product = product_result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_result = await session.execute(
        select(CartItem)
        .options(
            selectinload(CartItem.product)
            .selectinload(Product.category),
            selectinload(CartItem.product)
            .selectinload(Product.brand),
        )
        .where(CartItem.user_id == user.id, CartItem.product_id == item.product_id)
    )
    existing = cart_result.scalar_one_or_none()

    if existing:
        existing.quantity += item.quantity
    else:
        existing = CartItem(
            user_id=user.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        session.add(existing)

    await session.commit()

    result_with_relations = await session.execute(
        select(CartItem)
        .options(
            selectinload(CartItem.product)
            .selectinload(Product.category),
            selectinload(CartItem.product)
            .selectinload(Product.brand),
        )
        .where(CartItem.user_id == user.id, CartItem.product_id == item.product_id)
    )
    return result_with_relations.scalar_one()

@router.put("/getcart/{cart_item_id}", response_model=CartItemRead)
async def update_cart_item_by_id(
    cart_item_id: int,
    item: CartItemUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(CartItem)
        .options(
            selectinload(CartItem.product)
            .selectinload(Product.category),
            selectinload(CartItem.product)
            .selectinload(Product.brand),
        )
        .where(CartItem.id == cart_item_id, CartItem.user_id == user.id)
    )
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if item.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    if cart_item.product_id != item.product_id:
        raise HTTPException(status_code=400, detail="Product ID cannot be changed")

    cart_item.quantity = item.quantity
    await session.commit()
    await session.refresh(cart_item)

    return cart_item


@router.put("/me", response_model=CartItemRead)
async def update_cart_item_current_user(
    item: CartItemUpdate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    print(f"Received item: {item}")
    result = await session.execute(
        select(CartItem)
        .options(
            selectinload(CartItem.product)
            .selectinload(Product.category),
            selectinload(CartItem.product)
            .selectinload(Product.brand),
        )
        .where(CartItem.user_id == user.id, CartItem.product_id == item.product_id)
    )
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if item.quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    cart_item.quantity = item.quantity
    await session.commit()
    await session.refresh(cart_item)

    return cart_item

@router.delete("/me", status_code=204)
async def clear_cart_current_user(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(CartItem).where(CartItem.user_id == user.id)
    )
    items = result.scalars().all()

    for item in items:
        await session.delete(item)

    await session.commit()
    return None

@router.delete("/from_cart/{item_id}", status_code=204)
async def remove_from_cart(
    item_id: int, 
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
):
    result = await session.execute(select(CartItem).where(CartItem.id == item_id).where(CartItem.user_id == user.id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    await session.delete(item)
    await session.commit()
    return None