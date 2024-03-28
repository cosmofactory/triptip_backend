from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Base settings class to store all the configuration variables."""

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
