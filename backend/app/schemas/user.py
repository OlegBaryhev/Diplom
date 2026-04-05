from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    superuser = "superuser"
    moderator = "moderator"
    guest = "guest"


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    surname: Optional[str] = None
    role: Optional[UserRole] = UserRole.guest
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: int

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str