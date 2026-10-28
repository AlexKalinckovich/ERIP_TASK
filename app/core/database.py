from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_database_settings

_settings = get_database_settings()

engine = create_async_engine(
    str(_settings.database_url),
    echo=_settings.db_echo,
    pool_pre_ping=_settings.db_pool_pre_ping,
    pool_size=_settings.db_pool_size,
    max_overflow=_settings.db_max_overflow,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

async def dispose_engine() -> None:
    await engine.dispose()
