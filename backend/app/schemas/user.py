from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    surname: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role_id: Optional[int] = None

class UserRead(UserBase):
    id: int
    is_active: int
    role_id: Optional[int] = None
    permissions: Optional[Dict[str, Dict[str, List[str]]]] = None

    class Config:
        from_attributes = True