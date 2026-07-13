# Environment variables are read from the process environment.
# Locally, values can also be loaded from a .env file.

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DESCRIPTION_PATH = Path(__file__).resolve().parent.parent / "templates" / "api_description.md"


@lru_cache
def _load_description_template() -> str:
    return DESCRIPTION_PATH.read_text(encoding="utf-8")


class Settings(BaseSettings):

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    SQLALCHEMY_DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class FastAPISettings:
    title: str = "Task & Habit API"
    version: str = "1.0.0"
    created_by: str = "metthew"
    github_url: str = "https://github.com/MehdiKhoshnevisz/task-habit-api"

    @property
    def description(self) -> str:
        return (
            _load_description_template()
            .replace("{{created_by}}", self.created_by)
            .replace("{{github_url}}", self.github_url)
            .strip()
        )


settings = Settings()
fastapi_settings = FastAPISettings()
