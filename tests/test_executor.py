from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.executor import ScalarsError, SqlError, execute_sql


class FakeResult:
    def __init__(self, keys: list[str], rows: list[tuple[Any, ...]]) -> None:
        self._keys = keys
        self._rows = rows

    def keys(self) -> list[str]:
        return self._keys

    def fetchmany(self, size: int) -> list[tuple[Any, ...]]:
        return self._rows[:size]


class FakeSession:
    def __init__(self, result: FakeResult) -> None:
        self._result = result

    async def __aenter__(self) -> "FakeSession":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    async def execute(self, stmt) -> FakeResult:
        return self._result


class FakeSessionMaker:
    def __init__(self, result: FakeResult) -> None:
        self._result = result

    def __call__(self) -> FakeSession:
        return FakeSession(self._result)


def _session_maker(result: FakeResult) -> async_sessionmaker[AsyncSession]:
    return cast(async_sessionmaker[AsyncSession], FakeSessionMaker(result))


@pytest.mark.asyncio
async def test_execute_sql_returns_int() -> None:
    value = await execute_sql(
        "SELECT 1",
        session_maker=_session_maker(FakeResult(keys=["value"], rows=[(1,)])),
    )
    assert value == 1


@pytest.mark.asyncio
async def test_execute_sql_returns_float_from_decimal() -> None:
    value = await execute_sql(
        "SELECT 12.5",
        session_maker=_session_maker(
            FakeResult(keys=["value"], rows=[(Decimal("12.5"),)])
        ),
    )
    assert isinstance(value, float)
    assert value == 12.5


@pytest.mark.asyncio
async def test_execute_sql_rejects_empty_sql() -> None:
    with pytest.raises(SqlError):
        await execute_sql(
            "   \n\t  ",
            session_maker=_session_maker(FakeResult(keys=["value"], rows=[(1,)])),
        )


@pytest.mark.asyncio
async def test_execute_sql_rejects_semicolon() -> None:
    with pytest.raises(SqlError):
        await execute_sql(
            "SELECT 1; SELECT 2",
            session_maker=_session_maker(FakeResult(keys=["value"], rows=[(1,)])),
        )


@pytest.mark.asyncio
async def test_execute_sql_requires_one_column() -> None:
    with pytest.raises(ScalarsError):
        await execute_sql(
            "SELECT 1, 2",
            session_maker=_session_maker(FakeResult(keys=["a", "b"], rows=[(1, 2)])),
        )


@pytest.mark.asyncio
async def test_execute_sql_requires_one_row_zero_rows() -> None:
    with pytest.raises(ScalarsError):
        await execute_sql(
            "SELECT 1 WHERE 1=0",
            session_maker=_session_maker(FakeResult(keys=["value"], rows=[])),
        )


@pytest.mark.asyncio
async def test_execute_sql_requires_one_row_two_rows() -> None:
    with pytest.raises(ScalarsError):
        await execute_sql(
            "SELECT 1 UNION ALL SELECT 2",
            session_maker=_session_maker(FakeResult(keys=["value"], rows=[(1,), (2,)])),
        )


@pytest.mark.asyncio
async def test_execute_sql_rejects_bool_result() -> None:
    with pytest.raises(ScalarsError):
        await execute_sql(
            "SELECT TRUE",
            session_maker=_session_maker(FakeResult(keys=["value"], rows=[(True,)])),
        )
