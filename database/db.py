import os
import asyncpg
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Парсим DATABASE_URL
    url = urlparse(DATABASE_URL)
    DB_USER = url.username
    DB_PASSWORD = url.password
    DB_NAME = url.path[1:]
    DB_HOST = url.hostname
    DB_PORT = url.port
else:
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))

async def get_pool():
    return await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT
    )

async def init_db_schema():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(schema_sql)

async def register_user_if_not_exists(telegram_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (telegram_id) VALUES ($1)
            ON CONFLICT (telegram_id) DO NOTHING
            """,
            telegram_id
        )
