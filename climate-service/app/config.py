from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    version: str = "0.1.0"

    openweather_api_key: str = ""
    nasa_power_api_key: Optional[str] = None
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
    nasa_power_base_url: str = "https://power.larc.nasa.gov/api/v2"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/climate_service"
    redis_url: str = "redis://localhost:6379"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
