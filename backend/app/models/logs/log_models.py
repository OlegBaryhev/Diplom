from sqlalchemy import Column, Integer, String, DateTime, JSON, Index
from sqlalchemy.sql import func
from app.database import Base

class UserLog(Base):
    __tablename__ = "user_log"
    __table_args__ = (
        Index("ix_user_log_changed_at_operation", "changed_at", "operation"),
    )
    id = Column(Integer, primary_key=True)
    operation = Column(String(10), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    row_data = Column(JSON, nullable=False)

class CategoryLog(Base):
    __tablename__ = "category_log"
    __table_args__ = (
        Index("ix_category_log_changed_at_operation", "changed_at", "operation"),
    )
    id = Column(Integer, primary_key=True)
    operation = Column(String(10), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    row_data = Column(JSON, nullable=False)

class BrandLog(Base):
    __tablename__ = "brand_log"
    __table_args__ = (
        Index("ix_brand_log_changed_at_operation", "changed_at", "operation"),
    )
    id = Column(Integer, primary_key=True)
    operation = Column(String(10), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    row_data = Column(JSON, nullable=False)

class OrderLog(Base):
    __tablename__ = "order_log"
    __table_args__ = (
        Index("ix_order_log_changed_at_operation", "changed_at", "operation"),
    )
    id = Column(Integer, primary_key=True)
    operation = Column(String(10), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    row_data = Column(JSON, nullable=False)

class ProductLog(Base):
    __tablename__ = "product_log"
    __table_args__ = (
        Index("ix_product_log_changed_at_operation", "changed_at", "operation"),
    )
    id = Column(Integer, primary_key=True)
    operation = Column(String(10), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    row_data = Column(JSON, nullable=False)

class LogSettings(Base):
    __tablename__ = "log_settings"
    id = Column(Integer, primary_key=True)
    table_name = Column(String(50), unique=True, nullable=False)
    time_retention_minutes = Column(Integer, nullable=False)
    count_retention_limit = Column(Integer, nullable=False)