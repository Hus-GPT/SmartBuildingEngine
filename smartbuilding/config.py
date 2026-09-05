from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = (
        "postgresql+psycopg://smartbuilding:smartbuilding@localhost:5432/smartbuilding"
    )
    auto_create_schema: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
