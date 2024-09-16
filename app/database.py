from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os import getenv

# from sqlalchemy import create_engine  # for migration


SQLALCHEMY_DATABASE_URL = getenv("DATABASE_PUBLIC_URL", "")

Base = declarative_base()


# for migration
# Into .env remove +asyncpg
# engine_for_migration = create_engine(SQLALCHEMY_DATABASE_URL, future=True)


async_engine = create_async_engine(url=SQLALCHEMY_DATABASE_URL)
SessionLocal = async_sessionmaker(
    bind=async_engine, autoflush=False, expire_on_commit=False
)


async def create_session() -> AsyncSession:
    return SessionLocal()
