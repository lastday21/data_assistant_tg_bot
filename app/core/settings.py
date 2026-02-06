from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    tg_bot_token: str = Field(
        default="",
        alias="TG_BOT_TOKEN",
        min_length=1,
        validate_default=True,
    )

    level_logging: str = Field(default="INFO", alias="LEVEL_LOGGING")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")


def get_settings() -> Settings:
    return Settings()
