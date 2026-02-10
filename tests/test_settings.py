import pytest
from pydantic import ValidationError

from app.core.settings import Settings


def set_valid_env(monkeypatch: pytest.MonkeyPatch, **overrides: str) -> None:
    monkeypatch.setitem(Settings.model_config, "env_file", None)

    env = {
        "TG_BOT_TOKEN": "123:ABC",
        "DATABASE_URL": "postgresql+psycopg://app:app@localhost:5432/video",
    }
    env.update(overrides)

    for key, value in env.items():
        monkeypatch.setenv(key, value)


def test_settings_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    set_valid_env(monkeypatch)
    settings = Settings()
    assert settings.tg_bot_token
    assert settings.database_url


def test_settings_fails_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    set_valid_env(monkeypatch, TG_BOT_TOKEN="")
    with pytest.raises(ValidationError):
        Settings()


def test_settings_fails_without_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    set_valid_env(monkeypatch, DATABASE_URL="")
    with pytest.raises(ValidationError):
        Settings()


def test_settings_timeout_values(monkeypatch: pytest.MonkeyPatch) -> None:
    set_valid_env(
        monkeypatch,
        LLM_TIMEOUT_SECONDS="45",
        DB_TIMEOUT_SECONDS="20",
    )
    settings = Settings()
    assert settings.llm_timeout_seconds == 45
    assert settings.db_timeout_seconds == 20
