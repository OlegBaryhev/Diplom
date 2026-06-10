from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List
from enum import Enum

class UserRole(str, Enum):
    superuser = "superuser"
    moderator = "moderator"
    guest = "guest"

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
    role_name: Optional[str] = None
    permissions: Optional[Dict[str, Dict[str, List[str]]]] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str