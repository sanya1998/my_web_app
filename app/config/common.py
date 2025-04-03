from app.common.constants.environments import Environments
from app.common.constants.log_levels import LogLevel
from app.config.api import ApiSettings
from app.config.db import DbSettings
from app.config.email import EmailSettings
from app.config.grafana import GrafanaSettings
from app.config.hash import HashSettings
from pydantic_settings import SettingsConfigDict


class Settings(ApiSettings, DbSettings, HashSettings, EmailSettings, GrafanaSettings):
    ENVIRONMENT: Environments
    RELEASE_VERSION: str = "0.1.0"
    LOG_LEVEL: LogLevel
    SENTRY_DSN: str
    HAWK_TOKEN: str

    model_config = SettingsConfigDict(env_file="envs/base.env", env_file_encoding="utf-8")


settings = Settings()
