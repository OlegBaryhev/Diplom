from pydantic import BaseModel
from typing import Dict, List, Optional

class RoleBase(BaseModel):
    name: str
    permissions: Dict[str, Dict[str, List[str]]]

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    permissions: Optional[Dict[str, Dict[str, List[str]]]] = None

class RoleRead(RoleBase):
    id: int

    class Config:
        from_attributes = True