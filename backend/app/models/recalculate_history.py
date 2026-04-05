from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from sqlalchemy.sql import func

class RecalculateHistory(Base):
    __tablename__ = "recalculate_history"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    recalculated_by = Column(String, nullable=False)
    recalculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    parameters = Column(JSON, nullable=False)
