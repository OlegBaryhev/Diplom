from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

class Analog(Base):
    __tablename__ = "analogs"
    __table_args__ = (
        Index("ix_analogs_category_id", "category_id"),
        Index("ix_analogs_brand_id", "brand_id"),
        Index("ix_analogs_category_id_brand_id", "category_id", "brand_id"),
        Index("ix_analogs_price", "price"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)

    category = relationship("Category", back_populates="analogs")
    brand = relationship("Brand", back_populates="analogs")