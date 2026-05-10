import enum
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class UserRole(str, enum.Enum):
    superuser = "superuser"
    moderator = "moderator"
    guest = "guest"

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    is_active = Column(Integer, default=1)
    avatar_url = Column(String, nullable=True)

    role = relationship("Role")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

    @property
    def role_enum(self) -> UserRole | None:
        if self.role:
            return UserRole(self.role.name)
        return None

    def __getattr__(self, name):
        if name == "role":
            return self.role_enum
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")