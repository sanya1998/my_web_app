from pydantic_settings import BaseSettings


class HashSettings(BaseSettings):
    """
    Конфигурация хеширования
    """

    ENCODING: str = "utf-8"
    PASSWORD_MIN_LENGTH: int = 8
