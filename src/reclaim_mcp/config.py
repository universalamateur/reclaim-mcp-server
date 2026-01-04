"""Configuration settings for the Reclaim.ai MCP server."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="RECLAIM_")

    api_key: str
    base_url: str = "https://api.app.reclaim.ai"
    tool_profile: Literal["minimal", "standard", "full"] = "full"


def get_settings() -> Settings:
    """Get application settings from environment."""
    return Settings()  # type: ignore[call-arg]  # Reads from env vars
