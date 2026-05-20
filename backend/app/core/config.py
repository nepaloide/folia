from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    APP_NAME: str = "Folia API"
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/folia"
    )
    SECRET_KEY: str = ""
    GOOGLE_CLIENT_ID: str = ""
    CORS_ORIGINS: List[str] = ["*"]
    JWT_EXPIRATION_MINUTES: int = 43200

    @property
    def sync_database_url(self) -> str:
        """Return a sync-style URL for Alembic (without +asyncpg driver)."""
        return self.DATABASE_URL.replace("+asyncpg", "")


settings = Settings()
