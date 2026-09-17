from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    provider_base_url: HttpUrl = HttpUrl("https://jsonplaceholder.typicode.com")
    provider_timeout_seconds: float = Field(default=5.0, gt=0)
    max_concurrency: int = Field(default=5, gt=0)
    max_retry_attempts: int = Field(default=3, ge=1, le=3)
    allowed_cors_origins: list[str] = ["http://localhost:3000"]
