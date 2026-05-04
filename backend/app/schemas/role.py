from pydantic import BaseModel
from typing import Dict, List

class RoleBase(BaseModel):
    name: str
    permissions: Dict[str, Dict[str, List[str]]]

class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    id: int

    class Config:
        from_attributes = True