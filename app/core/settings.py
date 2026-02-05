from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    tg_bot_token: str | None = Field(default=None, alias="TG_BOT_TOKEN")


def get_settings() -> Settings:
    return Settings()
