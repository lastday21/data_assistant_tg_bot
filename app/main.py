import asyncio
import sys

from aiogram import Bot, Dispatcher

from app.bot.router import router
from app.core.logging import setup_logging
from app.core.settings import get_settings
from app.db.executor import execute_sql
from app.llm.client import YandexGptConfig, YandexGPTClient


async def main() -> None:
    settings = get_settings()
    setup_logging(level=settings.level_logging)

    bot = Bot(token=settings.tg_bot_token)

    llm_config = YandexGptConfig(
        api_key=settings.yandex_api_key,
        folder_id=settings.yandex_folder_id,
        timeout_seconds=settings.llm_timeout_seconds,
    )
    llm_client = YandexGPTClient(llm_config)

    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    await dispatcher.start_polling(
        bot,
        llm_request=llm_client.request_llm,
        sql_execute=execute_sql,
    )


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
