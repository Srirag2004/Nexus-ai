from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "NEXUS AI"
    app_env: Literal["development", "test", "qa", "production"] = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "sqlite+aiosqlite:///./nexus.db"
    sync_database_url: str = "sqlite:///./nexus.db"
    ai_provider: Literal["mock", "openai", "gemini"] = "mock"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.6-flash"
    github_token: str | None = None
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    google_oauth_client_id: str | None = None
    google_oauth_client_secret: str | None = None
    github_oauth_client_id: str | None = None
    github_oauth_client_secret: str | None = None
    auth_secret: str = "change-this-before-production"
    auth_token_hours: int = 168
    allowed_origins: str = "http://localhost:3000"
    max_upload_size_mb: int = 10
    default_user_id: str = Field(
        default="00000000-0000-0000-0000-000000000001",
        description="Single-user bootstrap id for local development.",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
