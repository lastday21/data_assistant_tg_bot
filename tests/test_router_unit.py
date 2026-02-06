from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Message

from app.bot.router import command_start, handle_text


@pytest.mark.asyncio
async def test_command_start_answers() -> None:
    answer = AsyncMock()
    message = cast(Message, SimpleNamespace(answer=answer))

    await command_start(message)

    answer.assert_awaited_once_with("Бот запущен. Напиши любой текст.")


@pytest.mark.asyncio
async def test_handle_text_answers() -> None:
    answer = AsyncMock()
    message = cast(Message, SimpleNamespace(text="привет", answer=answer))

    await handle_text(message)

    answer.assert_awaited_once_with("Ты написал привет")
