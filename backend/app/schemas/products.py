from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.category import CategoryRead
from app.schemas.brand import BrandRead

class ProductBase(BaseModel):
    name: str
    description: str
    price: int
    category_id: int
    brand_id: int

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int
    category: Optional[CategoryRead]
    brand: Optional[BrandRead]

    model_config = ConfigDict(from_attributes=True)
