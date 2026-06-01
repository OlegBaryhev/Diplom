import math
import time
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.dependencies import get_current_user
from app.database import get_session
from app.models.analogs import Analog
from app.models.products import Product
from app.models.recalculate_history import RecalculateHistory
from app.models.recalculation import Recalculation
from app.models.user import User, UserRole
from app.schemas.paginated import PaginatedResponse
from app.schemas.recalculation import (
    RecalculationCreate,
    RecalculationRead,
    RecalculationSearchRequest,
    RecalculationUpdate,
)

router = APIRouter()

RECALCULATION_TYPE_LABELS = {
    1: "Валютный курс",
    2: "Себестоимость + наценка",
    3: "Скидка по остаткам",
    4: "Цена аналогов",
    5: "Промо-период",
    6: "Накопительная скидка",
    7: "Красивые цены",
    8: "Скидка по рейтингу",
}


async def _select_products(session: AsyncSession, product_selection: dict) -> List[Product]:
    selection_type = product_selection.get("selection_type", "all")
    query = select(Product)

    if selection_type == "all":
        result = await session.execute(query)
        return list(result.scalars().all())

    if selection_type == "groups":
        category_ids = product_selection.get("category_ids", [])
        brand_ids = product_selection.get("brand_ids", [])
        if not category_ids and not brand_ids:
            result = await session.execute(query)
            return list(result.scalars().all())
        conditions = []
        if category_ids:
            conditions.append(Product.category_id.in_(category_ids))
        if brand_ids:
            conditions.append(Product.brand_id.in_(brand_ids))
        query = query.where(or_(*conditions))
        result = await session.execute(query)
        return list(result.scalars().all())

    if selection_type == "individual":
        mode = product_selection.get("mode", "include")
        product_ids = product_selection.get("product_ids", [])
        if mode == "include":
            if not product_ids:
                return []
            query = query.where(Product.id.in_(product_ids))
        else:
            if product_ids:
                query = query.where(Product.id.notin_(product_ids))
        result = await session.execute(query)
        return list(result.scalars().all())

    result = await session.execute(query)
    return list(result.scalars().all())


async def _execute_recalculation_logic(
    session: AsyncSession,
    recalc: Recalculation,
    executed_by: str,
) -> dict:
    start_ts = time.time()
    products = await _select_products(session, recalc.product_selection or {})
    params = recalc.parameters or {}
    affected = 0

    if recalc.recalculation_type == 1:
        old_rate = float(params.get("old_rate", 1) or 1)
        new_rate = float(params.get("new_rate", 1) or 1)
        if old_rate > 0:
            ratio = new_rate / old_rate
            for p in products:
                p.price = max(0, int(round(p.price * ratio)))
                affected += 1

    elif recalc.recalculation_type == 2:
        markup_percent = float(params.get("markup_percent", 0) or 0)
        markup_fixed = int(params.get("markup_fixed", 0) or 0)
        scope = params.get("scope", "global")
        scope_category_id = params.get("category_id")
        scope_brand_id = params.get("brand_id")
        for p in products:
            if scope == "category" and scope_category_id and p.category_id != scope_category_id:
                continue
            if scope == "brand" and scope_brand_id and p.brand_id != scope_brand_id:
                continue
            base = p.cost_price if p.cost_price else p.price
            p.price = max(0, int(round(base * (1 + markup_percent / 100) + markup_fixed)))
            affected += 1

    elif recalc.recalculation_type == 3:
        thresholds = sorted(
            params.get("thresholds", []),
            key=lambda x: x.get("stock_quantity", 0),
        )
        for p in products:
            extra = 0
            for threshold in thresholds:
                if p.stock_quantity <= threshold.get("stock_quantity", 0):
                    extra = threshold.get("extra_discount", 0)
                    break
            p.discount = min(100, max(0, p.discount + extra))
            affected += 1

    elif recalc.recalculation_type == 4:
        strategy = params.get("strategy", "cheaper_by")
        lower_by_percent = float(params.get("lower_by_percent", 5) or 5)
        markup = float(params.get("markup", 0) or 0)
        analog_result = await session.execute(select(Analog))
        all_analogs = list(analog_result.scalars().all())
        for p in products:
            cat_analogs = [a for a in all_analogs if a.category_id == p.category_id]
            if not cat_analogs:
                continue
            if strategy == "cheaper_by":
                min_price = min(a.price for a in cat_analogs)
                p.price = max(0, int(round(min_price * (1 - lower_by_percent / 100))))
            else:
                avg_price = sum(a.price for a in cat_analogs) / len(cat_analogs)
                p.price = max(0, int(round(avg_price * (1 + markup / 100))))
            affected += 1

    elif recalc.recalculation_type == 5:
        promo_discount = int(params.get("promo_discount", 0) or 0)
        max_discount = int(params.get("max_discount", 100) or 100)
        start_str = params.get("start_date", "")
        end_str = params.get("end_date", "")
        is_promo_active = True
        if start_str and end_str:
            try:
                start_dt = datetime.fromisoformat(start_str)
                end_dt = datetime.fromisoformat(end_str)
                now = datetime.now()
                is_promo_active = start_dt <= now <= end_dt
            except (ValueError, TypeError):
                pass
        for p in products:
            if is_promo_active:
                p.discount = min(max_discount, p.discount + promo_discount)
            affected += 1

    elif recalc.recalculation_type == 6:
        affected = 0

    elif recalc.recalculation_type == 7:
        step = float(params.get("step", 10) or 10)
        method = params.get("method", "ceil")
        if step <= 0:
            step = 1
        for p in products:
            if method == "ceil":
                p.price = int(math.ceil(p.price / step) * step)
            elif method == "floor":
                p.price = int(math.floor(p.price / step) * step)
            else:
                p.price = int(round(p.price / step) * step)
            affected += 1

    elif recalc.recalculation_type == 8:
        max_extra = int(params.get("max_extra", 20) or 20)
        min_rating = float(params.get("min_rating", 0) or 0)
        max_rating = float(params.get("max_rating", 5) or 5)
        rating_range = max_rating - min_rating
        for p in products:
            if rating_range > 0:
                normalized = max(0.0, min(1.0, (p.rating - min_rating) / rating_range))
                extra = int(normalized * max_extra)
            else:
                extra = 0
            p.discount = min(100, max(0, p.discount + extra))
            affected += 1

    await session.commit()

    exec_ms = int((time.time() - start_ts) * 1000)

    history = RecalculateHistory(
        name=recalc.name,
        description=recalc.description,
        recalculation_type=recalc.recalculation_type,
        trigger_type=recalc.trigger_type,
        recalculated_by=executed_by,
        parameters={
            "recalculation_id": recalc.id,
            "recalculation_type": recalc.recalculation_type,
            "parameters": params,
            "product_selection": recalc.product_selection,
        },
        products_affected_count=affected,
        execution_time_ms=exec_ms,
    )
    session.add(history)
    await session.commit()

    return {"products_affected_count": affected, "execution_time_ms": exec_ms}


@router.post("/search", response_model=PaginatedResponse[RecalculationRead])
async def search_recalculations(
    req: RecalculationSearchRequest,
    session: AsyncSession = Depends(get_session),
):
    conditions = []
    if req.search:
        conditions.append(Recalculation.name.ilike(f"%{req.search}%"))
    if req.recalculation_type is not None:
        conditions.append(Recalculation.recalculation_type == req.recalculation_type)
    if req.trigger_type:
        conditions.append(Recalculation.trigger_type == req.trigger_type)
    if req.is_active is not None:
        conditions.append(Recalculation.is_active == req.is_active)

    total = (
        await session.execute(
            select(func.count(Recalculation.id)).where(*conditions)
        )
    ).scalar_one()

    query = select(Recalculation).where(*conditions)

    if req.sort_by == "name_asc":
        query = query.order_by(Recalculation.name.asc())
    elif req.sort_by == "name_desc":
        query = query.order_by(Recalculation.name.desc())
    elif req.sort_by == "priority_asc":
        query = query.order_by(Recalculation.priority.asc())
    elif req.sort_by == "priority_desc":
        query = query.order_by(Recalculation.priority.desc())
    elif req.sort_by == "created_asc":
        query = query.order_by(Recalculation.created_at.asc())
    else:
        query = query.order_by(Recalculation.created_at.desc())

    query = query.offset((req.page - 1) * req.page_size).limit(req.page_size)
    result = await session.execute(query)
    return {"items": result.scalars().all(), "total": total}


@router.post("/", response_model=RecalculationRead)
async def create_recalculation(
    req: RecalculationCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    selection = req.product_selection.model_dump() if req.product_selection else {
        "selection_type": "all",
        "mode": "include",
        "product_ids": [],
        "category_ids": [],
        "brand_ids": [],
    }
    recalc = Recalculation(
        name=req.name,
        description=req.description,
        recalculation_type=req.recalculation_type,
        priority=req.priority,
        is_active=req.is_active,
        trigger_type=req.trigger_type,
        trigger_config=req.trigger_config,
        parameters=req.parameters,
        product_selection=selection,
    )
    session.add(recalc)
    await session.commit()
    await session.refresh(recalc)
    return recalc


@router.put("/{recalculation_id}", response_model=RecalculationRead)
async def update_recalculation(
    recalculation_id: int,
    req: RecalculationUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Recalculation).where(Recalculation.id == recalculation_id)
    )
    recalc = result.scalar_one_or_none()
    if not recalc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не найдено")

    if req.name is not None:
        recalc.name = req.name
    if req.description is not None:
        recalc.description = req.description
    if req.recalculation_type is not None:
        recalc.recalculation_type = req.recalculation_type
    if req.priority is not None:
        recalc.priority = req.priority
    if req.is_active is not None:
        recalc.is_active = req.is_active
    if req.trigger_type is not None:
        recalc.trigger_type = req.trigger_type
    if req.trigger_config is not None:
        recalc.trigger_config = req.trigger_config
    if req.parameters is not None:
        recalc.parameters = req.parameters
    if req.product_selection is not None:
        recalc.product_selection = req.product_selection.model_dump()

    await session.commit()
    await session.refresh(recalc)
    return recalc


@router.delete("/{recalculation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recalculation(
    recalculation_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Recalculation).where(Recalculation.id == recalculation_id)
    )
    recalc = result.scalar_one_or_none()
    if not recalc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не найдено")
    await session.delete(recalc)
    await session.commit()


@router.post("/{recalculation_id}/execute")
async def execute_recalculation(
    recalculation_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await session.execute(
        select(Recalculation).where(Recalculation.id == recalculation_id)
    )
    recalc = result.scalar_one_or_none()
    if not recalc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Не найдено")

    stats = await _execute_recalculation_logic(session, recalc, current_user.email)
    return {"success": True, **stats}


@router.get("/statistics")
async def get_recalculation_statistics(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")

    total_result = await session.execute(select(func.count(RecalculateHistory.id)))
    total = total_result.scalar_one()

    by_type_result = await session.execute(
        select(
            RecalculateHistory.recalculation_type,
            func.count(RecalculateHistory.id).label("count"),
        )
        .where(RecalculateHistory.recalculation_type.isnot(None))
        .group_by(RecalculateHistory.recalculation_type)
    )
    by_type = [
        {
            "type": row.recalculation_type,
            "count": row.count,
            "label": RECALCULATION_TYPE_LABELS.get(row.recalculation_type, f"Тип {row.recalculation_type}"),
        }
        for row in by_type_result.all()
    ]

    by_trigger_result = await session.execute(
        select(
            RecalculateHistory.trigger_type,
            func.count(RecalculateHistory.id).label("count"),
        )
        .where(RecalculateHistory.trigger_type.isnot(None))
        .group_by(RecalculateHistory.trigger_type)
    )
    trigger_labels = {"manual": "Ручной", "schedule": "По расписанию", "event": "По событию"}
    by_trigger = [
        {
            "trigger_type": row.trigger_type,
            "count": row.count,
            "label": trigger_labels.get(row.trigger_type, row.trigger_type),
        }
        for row in by_trigger_result.all()
    ]

    by_day_result = await session.execute(
        select(
            func.date_trunc("day", RecalculateHistory.recalculated_at).label("day"),
            func.count(RecalculateHistory.id).label("count"),
        )
        .group_by("day")
        .order_by("day")
        .limit(30)
    )
    by_day = [
        {
            "date": str(row.day.date()) if row.day else "",
            "count": row.count,
        }
        for row in by_day_result.all()
    ]

    avg_exec_result = await session.execute(
        select(func.avg(RecalculateHistory.execution_time_ms)).where(
            RecalculateHistory.execution_time_ms.isnot(None)
        )
    )
    avg_exec_ms = avg_exec_result.scalar_one()

    avg_affected_result = await session.execute(
        select(func.avg(RecalculateHistory.products_affected_count)).where(
            RecalculateHistory.products_affected_count.isnot(None)
        )
    )
    avg_affected = avg_affected_result.scalar_one()

    total_rules_result = await session.execute(select(func.count(Recalculation.id)))
    total_rules = total_rules_result.scalar_one()

    active_rules_result = await session.execute(
        select(func.count(Recalculation.id)).where(Recalculation.is_active == True)  # noqa: E712
    )
    active_rules = active_rules_result.scalar_one()

    return {
        "total_executions": total,
        "total_rules": total_rules,
        "active_rules": active_rules,
        "avg_execution_time_ms": round(float(avg_exec_ms or 0), 1),
        "avg_products_affected": round(float(avg_affected or 0), 1),
        "by_type": by_type,
        "by_trigger": by_trigger,
        "by_day": by_day,
    }
