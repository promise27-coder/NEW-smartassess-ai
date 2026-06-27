"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the SmartAssess AI backend."""

    app_name: str = Field(default="SmartAssess AI Backend")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    database_url: str = Field(
        default=(
            "postgresql+psycopg://smartassess_user:change_me@localhost:5432/"
            "smartassess_ai"
        )
    )
    resume_upload_dir: Path = Field(default=Path("storage/resumes"))
    resume_max_file_size_bytes: int = Field(default=10 * 1024 * 1024, gt=0)

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


settings = get_settings()
