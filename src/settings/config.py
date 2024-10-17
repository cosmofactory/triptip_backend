from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Base settings class to store all the configuration variables."""

    # Test settings
    MODE: Literal["DEV", "TEST", "PROD"]

    # Database settings
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_BUCKET_NAME: str = "triptip"

    SENTRY_KEY: str | None = None

    LOGFIRE_TOKEN: str | None = None
    SERVICE_NAME: str = "localtest"

    ALLOWED_CONTENT_TYPES: list[str] = [
        "image/jpeg",
        "image/gif",
        "image/png",
        "image/webp",
        "image/jpg",
    ]
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5 MB

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=".env",
    )


settings = Settings()
