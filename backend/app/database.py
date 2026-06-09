import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text(
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS discount INTEGER NOT NULL DEFAULT 0"
        ))
        await conn.execute(text(
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS cost_price INTEGER"
        ))
        await conn.execute(text(
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS stock_quantity INTEGER NOT NULL DEFAULT 0"
        ))
        await conn.execute(text(
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS rating DOUBLE PRECISION NOT NULL DEFAULT 0.0"
        ))
        await conn.execute(text(
            "ALTER TABLE recalculate_history ADD COLUMN IF NOT EXISTS recalculation_type INTEGER"
        ))
        await conn.execute(text(
            "ALTER TABLE recalculate_history ADD COLUMN IF NOT EXISTS trigger_type VARCHAR"
        ))
        await conn.execute(text(
            "ALTER TABLE recalculate_history ADD COLUMN IF NOT EXISTS products_affected_count INTEGER"
        ))
        await conn.execute(text(
            "ALTER TABLE recalculate_history ADD COLUMN IF NOT EXISTS execution_time_ms INTEGER"
        ))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_products_category_id ON products (category_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_products_brand_id ON products (brand_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_products_category_id_brand_id ON products (category_id, brand_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_products_price ON products (price)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_products_stock_quantity ON products (stock_quantity)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_products_rating ON products (rating)"))

        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_orders_user_id ON orders (user_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_orders_status ON orders (status)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_orders_created_at ON orders (created_at)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_orders_user_id_created_at ON orders (user_id, created_at)"))

        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_order_items_order_id ON order_items (order_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_order_items_product_id ON order_items (product_id)"))

        await conn.execute(text('CREATE INDEX IF NOT EXISTS ix_product_images_product_id_order ON product_images (product_id, "order")'))

        await conn.execute(text('CREATE INDEX IF NOT EXISTS ix_user_role_id ON "user" (role_id)'))
        await conn.execute(text('CREATE INDEX IF NOT EXISTS ix_user_is_active ON "user" (is_active)'))

        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_analogs_category_id ON analogs (category_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_analogs_brand_id ON analogs (brand_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_analogs_category_id_brand_id ON analogs (category_id, brand_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_analogs_price ON analogs (price)"))

        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_recalculations_is_active ON recalculations (is_active)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_recalculations_priority ON recalculations (priority)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_recalculations_recalculation_type ON recalculations (recalculation_type)"))

        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_recalculate_history_recalculated_at ON recalculate_history (recalculated_at)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_recalculate_history_recalculation_type ON recalculate_history (recalculation_type)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_recalculate_history_trigger_type ON recalculate_history (trigger_type)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_recalculate_history_type_trigger ON recalculate_history (recalculation_type, trigger_type)"))

        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_user_log_changed_at_operation ON user_log (changed_at, operation)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_category_log_changed_at_operation ON category_log (changed_at, operation)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_brand_log_changed_at_operation ON brand_log (changed_at, operation)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_order_log_changed_at_operation ON order_log (changed_at, operation)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_product_log_changed_at_operation ON product_log (changed_at, operation)"))

async def init_logs():
    sql_file = "sql/create_log_triggers.sql"
    async with engine.begin() as conn:
        raw_conn = await conn.get_raw_connection()
        async with raw_conn.driver_connection.transaction():
            with open(sql_file, "r", encoding="utf-8") as f:
                sql_script = f.read()
            await raw_conn.driver_connection.execute(sql_script)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session