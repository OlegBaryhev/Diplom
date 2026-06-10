import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

class UserRole(str, enum.Enum):
    superuser = "superuser"
    moderator = "moderator"
    guest = "guest"

class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        Index("ix_user_role_id", "role_id"),
        Index("ix_user_is_active", "is_active"),
    )

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    is_active = Column(Integer, default=1)
    avatar_url = Column(String, nullable=True)

    role_obj = relationship("Role", foreign_keys=[role_id])

    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

    @property
    def role(self) -> UserRole | None:
        if self.role_obj:
            return UserRole(self.role_obj.name)
        return None

    @property
    def role_name(self) -> str | None:
        if self.role_obj:
            return self.role_obj.name
        return None