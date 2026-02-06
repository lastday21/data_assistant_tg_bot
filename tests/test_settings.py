import pytest
from pydantic import ValidationError

from app.core.settings import Settings


def test_settings_reads_token_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    monkeypatch.setenv("TG_BOT_TOKEN", "123:ABC")

    settings = Settings()

    assert settings.tg_bot_token == "123:ABC"


def test_settings_raises_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    monkeypatch.delenv("TG_BOT_TOKEN", raising=False)

    with pytest.raises(ValidationError):
        Settings()
