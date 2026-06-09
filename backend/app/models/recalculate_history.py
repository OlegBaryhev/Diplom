from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.database import Base
from sqlalchemy.sql import func


class RecalculateHistory(Base):
    __tablename__ = "recalculate_history"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    recalculation_type = Column(Integer, nullable=True)
    trigger_type = Column(String, nullable=True)
    recalculated_by = Column(String, nullable=False)
    recalculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    parameters = Column(JSON, nullable=False)
    products_affected_count = Column(Integer, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
