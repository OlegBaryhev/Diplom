from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime
from app.models.order import OrderStatus
from app.schemas.user import UserRead

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


class OrderItemRead(BaseModel):
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class OrderRead(BaseModel):
    id: int
    user_id: int
    user: UserRead
    status: OrderStatus
    created_at: datetime
    pickup_code: str
    items: List[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)
