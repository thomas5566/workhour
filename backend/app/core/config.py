from functools import lru_cache
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or ``.env``."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "WorkHour API"
    PROJECT_VERSION: str = "1.0.0"

    DATABASE_URL: str = Field(min_length=1)
    SECRET_KEY: str = Field(min_length=32)
    # A single shared SECRET_KEY supports HMAC JWT algorithms, not `none` or RSA.
    ALGORITHM: Literal["HS256", "HS384", "HS512"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)
    ENABLE_API_DOCS: bool = True

    BACKEND_CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:8080",
            "http://localhost:5173",
        ]
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def reject_placeholder_secret(cls, value: str) -> str:
        # A copied .env.example must fail closed until its placeholder changes.
        if value.strip().lower() == "replace-with-a-long-random-secret":
            raise ValueError("SECRET_KEY must not use the example placeholder")
        return value

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def normalize_cors_origins(cls, origins: list[str]) -> list[str]:
        normalized: list[str] = []
        for raw_origin in origins:
            origin = raw_origin.strip()
            parsed = urlsplit(origin)
            if (
                "*" in origin
                or parsed.scheme not in {"http", "https"}
                or not parsed.netloc
                or parsed.path not in {"", "/"}
                or parsed.query
                or parsed.fragment
                or parsed.username
                or parsed.password
            ):
                raise ValueError(
                    "CORS origins must be explicit HTTP(S) origins without "
                    "paths, credentials, queries, fragments, or wildcards"
                )

            normalized_origin = f"{parsed.scheme}://{parsed.netloc}"
            if normalized_origin not in normalized:
                normalized.append(normalized_origin)
        return normalized


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
