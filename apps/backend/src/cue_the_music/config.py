"""Application settings loaded from environment variables / .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for Cue the Music.

    Values are loaded from environment variables or a .env file.
    DISCOGS_TOKEN and DISCOGS_USERNAME are required for Discogs integration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DISCOGS_TOKEN: str
    DISCOGS_USERNAME: str
    HOST_PIN: str = "0000"


def get_settings() -> Settings:
    """FastAPI dependency that provides application settings.

    Raises ValidationError at startup if required env vars are missing.
    """
    return Settings()  # type: ignore[call-arg]
