from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.session import session_factory


class ModuleError(Exception):
    pass


class ScalarsError(ModuleError):
    pass


class SqlError(ModuleError):
    pass


_FORBIDDEN_TOKENS = re.compile(
    r"\b("
    r"insert|update|delete|drop|alter|truncate|create|grant|revoke|"
    r"copy|call|do|execute|set|show|listen|notify|vacuum|analyze"
    r")\b",
    re.IGNORECASE,
)


def _validation_sql(sql: str) -> None:
    if not sql.strip():
        raise SqlError("sql пустой")

    if ";" in sql:
        raise SqlError("Запрещены ';' (только один SQL-оператор)")

    if _FORBIDDEN_TOKENS.search(sql):
        raise SqlError("Запрещены DDL/DML/utility команды в SQL")


def _validation_result(value: Any) -> int | float:
    if isinstance(value, bool):
        raise ScalarsError("SQL вернул bool, нужно число")

    if isinstance(value, int) or isinstance(value, float):
        return value

    if isinstance(value, Decimal):
        return float(value)

    raise ScalarsError(f"SQL вернул тип {type(value).__name__}, нужно число")


async def execute_sql(
    sql, *, session_maker: async_sessionmaker[AsyncSession] = session_factory
) -> int | float:
    _validation_sql(sql)

    async with session_maker() as session:
        result = await session.execute(text(sql))

        keys = list(result.keys())
        if len(keys) != 1:
            raise ScalarsError(f"Ожидалась 1 колонка, а получили {len(keys)}")

        rows = result.fetchmany(2)
        if len(rows) != 1:
            raise ScalarsError(f"Ожидалась 1 строка, а получили {len(rows)}")

        return _validation_result(rows[0][0])
