from pydantic_settings import SettingsConfigDict

from app.config.api import ApiSettings
from app.config.db import DbSettings


class Settings(ApiSettings, DbSettings):
    TEST: bool = False

    model_config = SettingsConfigDict(env_file=".envs/local.env", env_file_encoding="utf-8")


settings = Settings()
