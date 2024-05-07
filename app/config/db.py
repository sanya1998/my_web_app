from typing import Optional

from pydantic import field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings


class DbSettings(BaseSettings):
    """
    Конфигурация базы данных
    """

    POSTGRES_VERSION: float

    DB_DRIVER: str = "postgresql+asyncpg"

    DB_HOST: str
    DB_PORT: int

    DB_USER: str
    DB_PASSWORD: str

    DB_NAME: str

    DB_URL: Optional[str] = None

    DB_WRITE_MIN_POOL_SIZE: int = 4
    DB_WRITE_MAX_POOL_SIZE: int = 10

    DB_READ_MIN_POOL_SIZE: int = 5
    DB_READ_MAX_POOL_SIZE: int = 20

    DB_COMMAND_TIMEOUT: float = 10.0

    @field_validator("DB_URL")
    @classmethod
    def get_db_url(cls, value: Optional[str], info: FieldValidationInfo):
        if value is None:
            value = (
                f"{info.data['DB_DRIVER']}://"
                f"{info.data['DB_USER']}:{info.data['DB_PASSWORD']}@"
                f"{info.data['DB_HOST']}:{info.data['DB_PORT']}/"
                f"{info.data['DB_NAME']}"
            )
        return value
