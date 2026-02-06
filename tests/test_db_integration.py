import psycopg
import pytest

from app.core.settings import get_settings


pytestmark = pytest.mark.integration


def _normalize_dsn(dsn: str) -> str:
    if dsn.startswith("postgresql+psycopg://"):
        return "postgresql://" + dsn.split("://", 1)[1]
    return dsn


@pytest.mark.asyncio
async def test_db_smoke() -> None:
    settings = get_settings()
    dsn_raw = settings.database_url
    if not dsn_raw:
        pytest.skip("DATABASE_URL is not set")

    dsn = _normalize_dsn(dsn_raw)

    conn = await psycopg.AsyncConnection.connect(dsn)
    async with conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT 1;")
            row = await cur.fetchone()
            assert row == (1,)
