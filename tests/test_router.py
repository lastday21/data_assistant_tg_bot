import pytest

from app.bot.router import handle_text


class FakeMessage:
    def __init__(self, text: str) -> None:
        self.text = text
        self.answers: list[str] = []

    async def answer(self, text: str) -> None:
        self.answers.append(text)


@pytest.mark.asyncio
async def test_handle_text_success() -> None:
    async def fake_llm_request(messages: list[dict[str, str]]) -> str:
        assert messages
        return "SELECT 1"

    async def fake_sql_execute(sql: str) -> int:
        assert sql == "SELECT 1"
        return 1

    message = FakeMessage("сколько?")

    await handle_text(message, fake_llm_request, fake_sql_execute)

    assert message.answers == ["1"]


@pytest.mark.asyncio
async def test_handle_text_returns_unified_error() -> None:
    async def fake_llm_request(messages: list[dict[str, str]]) -> str:
        raise RuntimeError("boom")

    async def fake_sql_execute(sql: str) -> int:
        return 1

    message = FakeMessage("сколько?")

    await handle_text(message, fake_llm_request, fake_sql_execute)

    assert message.answers == ["Не смог обработать запрос"]
