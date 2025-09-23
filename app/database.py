from os import getenv

from dotenv import load_dotenv

# from sqlalchemy import create_engine  # for migration
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Cargar variables de entorno desde el archivo .env
load_dotenv()

SQLALCHEMY_DATABASE_URL = getenv("DATABASE_PUBLIC_URL", "")


class Base(DeclarativeBase):
    pass


# for migration
# Into .env remove +asyncpg
# engine_for_migration = create_engine(SQLALCHEMY_DATABASE_URL, future=True)


async_engine = create_async_engine(url=SQLALCHEMY_DATABASE_URL)
SessionLocal = async_sessionmaker(
    bind=async_engine, autoflush=False, expire_on_commit=False
)


async def create_session() -> AsyncSession:
    return SessionLocal()
