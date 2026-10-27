import os
from functools import lru_cache

from pydantic import Field, HttpUrl
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
