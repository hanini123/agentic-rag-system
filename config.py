"""
Configuration Module

Handles environment variables and API keys securely using Pydantic Settings.

Why this matters:
-----------------
- Keeps secrets out of code
- Enables easy configuration across environments
- Industry best practice for production systems
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from .env file.

    Attributes:
        nvidia_api_key (str): API key for NVIDIA LLM endpoint
        tavily_api_key (str): API key for Tavily search
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    nvidia_api_key: str
    tavily_api_key: str


# Global settings instance
settings = Settings()  # Loaded automatically from .env