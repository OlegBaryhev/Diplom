from pydantic import BaseModel
from typing import Optional, List
from app.models.order import OrderStatus
from datetime import date


class OrderSearchRequest(BaseModel):
    search: Optional[str] = None
    statuses: Optional[List[OrderStatus]] = None
    user_id: Optional[int] = None
    created_from: Optional[date] = None
    created_to: Optional[date] = None
    quantity_from: Optional[int] = None
    quantity_to: Optional[int] = None
    sort_by: Optional[str] = None
    page: int = 1
    page_size: int = 100