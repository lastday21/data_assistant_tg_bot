from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

_session_factory: async_sessionmaker[AsyncSession] | None = None


def build_engine(database_url: str, db_timeout_seconds: float = 15.0) -> AsyncEngine:
    timeout_ms = int(db_timeout_seconds * 1000)
    options = f"-c statement_timeout={timeout_ms}"

    return create_async_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"options": options},
    )


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        from app.core.settings import get_settings

        settings = get_settings()
        engine = build_engine(settings.database_url, settings.db_timeout_seconds)
        _session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    return _session_factory
