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
        # Idempotent column addition for fields added after initial schema
        await conn.execute(text(
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS discount INTEGER NOT NULL DEFAULT 0"
        ))

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