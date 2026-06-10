from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Index
from app.database import Base
from sqlalchemy.sql import func


class Recalculation(Base):
    __tablename__ = "recalculations"
    __table_args__ = (
        Index("ix_recalculations_is_active", "is_active"),
        Index("ix_recalculations_priority", "priority"),
        Index("ix_recalculations_recalculation_type", "recalculation_type"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    recalculation_type = Column(Integer, nullable=False)
    priority = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    trigger_type = Column(String, nullable=False, default="manual")
    trigger_config = Column(JSON, nullable=True)
    parameters = Column(JSON, nullable=False, default=dict)
    product_selection = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
