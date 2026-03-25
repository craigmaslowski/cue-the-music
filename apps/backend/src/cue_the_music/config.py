"""Application settings loaded from environment variables / .env file."""

import logging
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Resolve .env relative to the backend package root (three .parent hops from this file)
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    """Central configuration for Cue the Music.

    Values are loaded from environment variables or a .env file.
    DISCOGS_TOKEN and DISCOGS_USERNAME are required for Discogs integration.
    """

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DISCOGS_TOKEN: str
    DISCOGS_USERNAME: str
    HOST_PIN: str = "0000"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """FastAPI dependency that provides application settings.

    Raises ValidationError at startup if required env vars are missing.
    """
    settings = Settings()  # type: ignore[call-arg]
    if _ENV_FILE.is_file():
        logger.info("Loaded settings from %s", _ENV_FILE)
    else:
        logger.warning(
            "No .env file found at %s — using env vars / defaults", _ENV_FILE
        )
    return settings
