import asyncio
import sys

import pytest
from aiogram import Dispatcher

from app.bot.router import router

if sys.platform == "win32" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="session")
def dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(router)
    return dp
