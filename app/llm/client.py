from __future__ import annotations

from dataclasses import dataclass

import aiohttp


class LlmClientError(Exception):
    pass


@dataclass(frozen=True)
class YandexGptConfig:
    api_key: str
    folder_id: str
    endpoint_url: str = (
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    )
    temperature: float = 0.0
    max_tokens: int = 800
    timeout_seconds: float = 30.0


class YandexGPTClient:
    def __init__(self, config: YandexGptConfig) -> None:
        self._config = config

    async def request_llm(self, messages: list[dict[str, str]]) -> str:
        if not self._config.api_key.strip():
            raise LlmClientError("YANDEX_API_KEY is empty")
        if not self._config.folder_id.strip():
            raise LlmClientError("YANDEX_FOLDER_ID is empty")

        payload = {
            "modelUri": f"gpt://{self._config.folder_id}/yandexgpt/rc",
            "completionOptions": {
                "stream": False,
                "temperature": self._config.temperature,
                "maxTokens": str(self._config.max_tokens),
            },
            "messages": messages,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self._config.api_key}",
        }

        timeout = aiohttp.ClientTimeout(total=self._config.timeout_seconds)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                self._config.endpoint_url,
                json=payload,
                headers=headers,
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise LlmClientError(f"YandexGPT error {response.status}: {text}")

                data = await response.json()

        alternatives = data.get("alternatives")
        if not alternatives:
            raise LlmClientError(f"Empty alternatives: {data}")

        message = alternatives[0].get("message") or {}
        text = (message.get("text") or "").strip()
        if not text:
            raise LlmClientError(f"Empty message text: {data}")

        sql = text.strip()

        if sql.startswith("```"):
            sql = sql.strip("`").strip()

        if sql.endswith(";"):
            sql = sql[:-1].rstrip()

        return sql
