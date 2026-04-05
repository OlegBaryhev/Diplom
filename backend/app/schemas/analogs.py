from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.category import CategoryRead
from app.schemas.brand import BrandRead

class AnalogBase(BaseModel):
    name: str
    description: str
    price: int
    category_id: int
    brand_id: int

class AnalogCreate(AnalogBase):
    pass

class AnalogRead(AnalogBase):
    id: int
    category: Optional[CategoryRead]
    brand: Optional[BrandRead]

    model_config = ConfigDict(from_attributes=True)
