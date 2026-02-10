from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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

        request_payload: dict[str, Any] = {
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

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self._config.endpoint_url,
                    json=request_payload,
                    headers=headers,
                ) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise LlmClientError(
                            f"YandexGPT error {response.status}: {text}"
                        )

                    data: dict[str, Any] = await response.json(content_type=None)
        except TimeoutError as exc:
            raise LlmClientError("LLM request timeout") from exc

        result = data.get("result")
        response_payload = result if isinstance(result, dict) else data

        alternatives = response_payload.get("alternatives")
        if not isinstance(alternatives, list) or not alternatives:
            raise LlmClientError(f"Empty alternatives: {response_payload}")

        first_alt = alternatives[0]
        if not isinstance(first_alt, dict):
            raise LlmClientError(f"Invalid alternative: {first_alt!r}")

        message = first_alt.get("message")
        message_dict = message if isinstance(message, dict) else {}

        text_value = message_dict.get("text")
        text = text_value.strip() if isinstance(text_value, str) else ""
        if not text:
            raise LlmClientError(f"Empty message text: {response_payload}")

        sql = text

        if sql.startswith("```"):
            lines = sql.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            sql = "\n".join(lines).strip()

        if sql.endswith(";"):
            sql = sql[:-1].rstrip()

        return sql
