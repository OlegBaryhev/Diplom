from pydantic import BaseModel, ConfigDict

class CategoryBase(BaseModel):
    name: str
    description: str


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
