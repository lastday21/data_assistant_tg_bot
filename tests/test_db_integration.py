import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.settings import get_settings
from app.db.session import build_engine


pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_db_smoke() -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL is not set")

    engine = build_engine(settings.database_url)
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        result = await session.execute(text("SELECT 1;"))
        assert result.scalar_one() == 1

    await engine.dispose()
