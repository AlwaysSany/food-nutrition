"""
Configuration management for the MCP server.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
import structlog

logger = structlog.get_logger(__name__)


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, json_schema_extra={"env": "DEBUG"})
    LOG_LEVEL: str = Field(default="INFO", json_schema_extra={"env": "LOG_LEVEL"})
    
    # API Keys
    USDA_API_KEY: str = Field(default="", json_schema_extra={"env": "USDA_API_KEY"})
    NUTRITIONIX_APP_ID: str = Field(default="", json_schema_extra={"env": "NUTRITIONIX_APP_ID"})
    NUTRITIONIX_APP_KEY: str = Field(default="", json_schema_extra={"env": "NUTRITIONIX_APP_KEY"})
    
    # API Configuration
    USDA_BASE_URL: str = "https://api.nal.usda.gov/fdc/v1"
    NUTRITIONIX_BASE_URL: str = "https://trackapi.nutritionix.com/v2"
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = Field(default=60, json_schema_extra={"env": "MAX_REQUESTS_PER_MINUTE"})
    CACHE_TTL: int = Field(default=3600, json_schema_extra={"env": "CACHE_TTL"})  # 1 hour
    
    # Request Configuration
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3

    model_config = ConfigDict(env_file=".env",extra='ignore', env_file_encoding="utf-8", case_sensitive=True)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings()
        logger.info("Settings loaded", debug=_settings.DEBUG, log_level=_settings.LOG_LEVEL)
    return _settings


def validate_api_keys() -> dict[str, bool]:
    """Validate that required API keys are present."""
    settings = get_settings()
    
    validation_results = {
        "usda": bool(settings.USDA_API_KEY),
        "edamam": bool(settings.EDAMAM_APP_ID and settings.EDAMAM_APP_KEY),
        "nutritionix": bool(settings.NUTRITIONIX_APP_ID and settings.NUTRITIONIX_APP_KEY),
    }
    
    logger.info("API key validation", results=validation_results)
    return validation_results
