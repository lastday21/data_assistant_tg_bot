from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name=__name__)


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    await message.answer("Бот запущен. Напиши любой текст.")


@router.message(F.text)
async def handle_text(message: Message) -> None:
    await message.answer(f"Ты написал {message.text}")
