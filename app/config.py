import os
from functools import lru_cache

from pydantic import Field, HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_env_file() -> str:
    environment = os.getenv("ENVIRONMENT", "test").strip().lower()
    return ".env.prod" if environment in {"prod", "production"} else ".env.test"


class NBRBSettings(BaseSettings):
    api_base_url: HttpUrl = Field(default="https://api.nbrb.by/")
    timeout: float = Field(default=5.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
    retry_backoff: float = Field(default=0.5, ge=0)
    retry_jitter: float = Field(default=0.1, ge=0)

    model_config = SettingsConfigDict(
        env_prefix="NBRB_",
        env_file=_default_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
    )


@lru_cache
def get_nbrb_settings() -> NBRBSettings:
    return NBRBSettings()


class DatabaseSettings(BaseSettings):
    database_url: PostgresDsn
    db_echo: bool = False
    db_pool_pre_ping: bool = True
    db_pool_size: int = Field(default=10, gt=0)
    db_max_overflow: int = Field(default=20, ge=0)

    model_config = SettingsConfigDict(
        env_file=_default_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
    )


@lru_cache
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()


class DealSettings(BaseSettings):
    ttl_minutes: int = Field(default=15, gt=0)

    model_config = SettingsConfigDict(
        env_prefix="DEAL_",
        env_file=_default_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
    )


@lru_cache
def get_deal_settings() -> DealSettings:
    return DealSettings()
