from typing import Any, Callable, Set

from pydantic import (
    AliasChoices,
    AmqpDsn,
    BaseModel,
    Field,
    ImportString,
    PostgresDsn,
    RedisDsn,
)

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_installation_id: int = Field()
    app_private_key: str = Field()
    repo_name: str = Field()
    base_branch: str = Field()
    app_id: str = Field()
    app_client_id: str = Field()
    app_client_secrets: str = Field()
    webhook_token: str = Field()
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
