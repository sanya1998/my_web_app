from app.common.constants.environments import Environments
from app.common.constants.log_levels import LogLevel
from app.config.api import ApiSettings
from app.config.celery import CelerySettings
from app.config.db import DbSettings
from app.config.email import EmailSettings
from app.config.hash import HashSettings
from pydantic_settings import SettingsConfigDict


class Settings(ApiSettings, DbSettings, HashSettings, CelerySettings, EmailSettings):
    ENVIRONMENT: Environments
    RELEASE_VERSION: str = "0.1.0"
    LOG_LEVEL: LogLevel
    SENTRY_DSN: str

    # Пока celery запускается из консоли, это нужно, так как не удалось подцепить env-файл
    model_config = SettingsConfigDict(env_file="envs/local.env", env_file_encoding="utf-8")


settings = Settings()
