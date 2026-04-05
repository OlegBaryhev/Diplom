from pydantic import BaseModel, ConfigDict
from datetime import datetime

class BrandBase(BaseModel):
    name: str
    description: str

class BrandCreate(BrandBase):
    pass

class BrandRead(BrandBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
