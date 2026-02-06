import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot.router import router
from app.core.settings import get_settings


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    setting = get_settings()
    token = setting.tg_bot_token

    bot = Bot(token=token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
