from typing import Awaitable, Callable, cast
import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.llm.prompt import build_messages

router = Router(name=__name__)
logger = logging.getLogger(__name__)


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

    logger.info("input_text=%s", text)

    try:
        messages = build_messages(text)
        sql = await llm_request(messages)
        value = await sql_execute(sql)
    except Exception:
        logger.exception("failed_to_process_request")
        await message.answer("Не смог обработать запрос")
        return

    await message.answer(str(value))
