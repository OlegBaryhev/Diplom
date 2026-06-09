from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from app.schemas.category import CategoryRead
from app.schemas.brand import BrandRead


class ProductImageRead(BaseModel):
    id: int
    url: str
    is_primary: bool
    order: int

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str
    description: str
    price: int
    category_id: int
    brand_id: int
    discount: int = 0
    cost_price: Optional[int] = None
    stock_quantity: int = 0
    rating: float = 0.0

    @field_validator("discount")
    @classmethod
    def validate_discount(cls, v: int) -> int:
        if not 0 <= v <= 100:
            raise ValueError("Скидка должна быть от 0 до 100")
        return v


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int
    category: Optional[CategoryRead] = None
    brand: Optional[BrandRead] = None
    images: list[ProductImageRead] = []

    model_config = ConfigDict(from_attributes=True)
