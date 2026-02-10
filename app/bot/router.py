from typing import Awaitable, Callable, cast

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.llm.prompt import build_messages

router = Router(name=__name__)


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    await message.answer("Бот запущен. Напиши любой текст.")


@router.message(F.text)
async def handle_text(
    message: Message,
    llm_request: Callable[[list[dict[str, str]]], Awaitable[str]],
    sql_execute: Callable[[str], Awaitable[int | float]],
) -> None:
    text = cast(str, message.text)

    messages = build_messages(text)
    sql = await llm_request(messages)
    value = await sql_execute(sql)

    await message.answer(str(value))
