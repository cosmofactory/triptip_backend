from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = ".env"


class EmailServiceSettings(BaseSettings):
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str
    SMTP_STARTTLS: bool
    SMTP_SSL_TLS: bool

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_prefix="EMAIL_", extra="ignore")


class Settings(BaseSettings):
    """Base settings class to store all the configuration variables."""

    PROJECT_NAME: str = "TripTip"

    VERIFICATION_URL: str = "https://triptip.pro/verify"

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
    EMAIL_VERIFICATION_EXPIRATION_HOURS: int = 24
    USER_DAILY_LIMIT: int = 20
    GLOBAL_DAILY_LIMIT: int = 2000

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_BUCKET_NAME: str = "triptip"

    AWS_CLOUDFRONT_DISTRIBUTION: str = "d1khyh6wja0468.cloudfront.net"

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

    email_service: EmailServiceSettings = EmailServiceSettings()

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore",
    )


settings = Settings()
