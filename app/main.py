import asyncio

from aiogram import Bot, Dispatcher

from app.bot.router import router
from app.core.logging import setup_logging
from app.core.settings import get_settings


async def main() -> None:
    settings = get_settings()
    setup_logging(level=settings.level_logging)
    token = settings.tg_bot_token

    bot = Bot(token=token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
