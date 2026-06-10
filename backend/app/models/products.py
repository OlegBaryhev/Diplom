from sqlalchemy import Column, Integer, String, ForeignKey, Float, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_category_id", "category_id"),
        Index("ix_products_brand_id", "brand_id"),
        Index("ix_products_category_id_brand_id", "category_id", "brand_id"),
        Index("ix_products_price", "price"),
        Index("ix_products_stock_quantity", "stock_quantity"),
        Index("ix_products_rating", "rating"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    discount = Column(Integer, nullable=False, default=0)
    cost_price = Column(Integer, nullable=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    rating = Column(Float, nullable=False, default=0.0)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)

    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.order",
    )
