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

    level_logging: str = Field(
        default="INFO",
        alias="LEVEL_LOGGING",
    )

    database_url: str = Field(
        default="",
        alias="DATABASE_URL",
        min_length=1,
        validate_default=True,
    )
    yandex_api_key: str = Field(default="", alias="YANDEX_API_KEY")
    yandex_folder_id: str = Field(default="", alias="YANDEX_FOLDER_ID")
    llm_timeout_seconds: float = Field(default=30.0, alias="LLM_TIMEOUT_SECONDS")
    db_timeout_seconds: float = Field(default=15.0, alias="DB_TIMEOUT_SECONDS")


def get_settings() -> Settings:
    return Settings()
