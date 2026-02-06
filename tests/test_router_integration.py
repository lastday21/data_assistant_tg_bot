import datetime
from unittest.mock import AsyncMock

import pytest
from aiogram import Bot, Dispatcher
from aiogram.types import Chat, Message, Update, User

pytestmark = pytest.mark.integration


def build_update(text: str, update_id: int) -> Update:
    user = User(id=1, is_bot=False, first_name="Test")
    chat = Chat(id=1, type="private")
    message = Message(
        message_id=1,
        date=datetime.datetime.now(datetime.timezone.utc),
        chat=chat,
        from_user=user,
        text=text,
    )
    return Update(update_id=update_id, message=message)


@pytest.mark.asyncio
async def test_integration_start(
    dispatcher: Dispatcher, monkeypatch: pytest.MonkeyPatch
) -> None:
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    bot = Bot(token="42:TEST")
    update = build_update("/start", update_id=100)

    await dispatcher.feed_update(bot, update)

    answer_mock.assert_any_await("Бот запущен. Напиши любой текст.")
    await bot.session.close()


@pytest.mark.asyncio
async def test_integration_text(
    dispatcher: Dispatcher, monkeypatch: pytest.MonkeyPatch
) -> None:
    answer_mock = AsyncMock()
    monkeypatch.setattr(Message, "answer", answer_mock)

    bot = Bot(token="42:TEST")
    update = build_update("привет", update_id=101)

    await dispatcher.feed_update(bot, update)

    answer_mock.assert_any_await("Ты написал привет")
    await bot.session.close()
