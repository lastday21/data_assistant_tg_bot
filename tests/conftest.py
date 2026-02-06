import pytest
from aiogram import Dispatcher

from app.bot.router import router


@pytest.fixture(scope="session")
def dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(router)
    return dp
