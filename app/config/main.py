from app.config.api import ApiSettings
from app.config.db import DbSettings
from app.config.hash import HashSettings
from pydantic_settings import SettingsConfigDict


class Settings(ApiSettings, DbSettings, HashSettings):
    TEST: bool = False

    model_config = SettingsConfigDict(env_file=".envs/local.env", env_file_encoding="utf-8")


settings = Settings()
