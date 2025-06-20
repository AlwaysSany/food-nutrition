import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # API Keys
    nutritionix_api_key: Optional[str] = None
    nutritionix_app_id: Optional[str] = None
    edamam_api_key: Optional[str] = None
    edamam_app_id: Optional[str] = None
    usda_api_key: Optional[str] = None
    spoonacular_api_key: Optional[str] = None

    # Server Configuration
    server_name: str = "food-nutrition-intelligence"
    server_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Rate Limiting
    api_rate_limit: int = 100
    api_rate_limit_period: int = 3600

    # Cache Settings
    cache_ttl: int = 3600
    enable_cache: bool = True

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
