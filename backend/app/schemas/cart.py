from pydantic import BaseModel, ConfigDict
from app.schemas.products import ProductRead
from app.schemas.user import UserRead
from typing import Optional, List

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int


class CartItemRead(BaseModel):
    id: int
    user_id: int
    product_id: int
    product: ProductRead
    quantity: int

    model_config = ConfigDict(from_attributes=True)

class CartSearchRequest(BaseModel):
    search: Optional[str] = None
    sort_by: Optional[str] = None


class CartSummary(BaseModel):
    id: int
    total_price: int
    user: UserRead
    products_total: int

    model_config = ConfigDict(from_attributes=True)

class CartItemUpdate(BaseModel):
    product_id: int
    quantity: int
    