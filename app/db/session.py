from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, create_async_engine

from app.core.settings import get_settings


def build_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url, pool_pre_ping=True)


settings = get_settings()

engine = build_engine(settings.database_url)

session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
