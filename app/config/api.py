from typing import List

from pydantic_settings import BaseSettings


class ApiSettings(BaseSettings):
    """
    Базовые настройки api приложения
    """

    APPLICATION_NAME: str = "My web application"
    APPLICATION_DESCRIPTION: str = "My web application description"
    HOST: str = "localhost"
    PORT: int = 8000
    SWAGGER_UI_PARAMETERS: dict = {"tryItOutEnabled": True}
    DEBUG: bool = True
    LIMIT_DEFAULT: int = 10
    LIMIT_MAX: int = 100
    OFFSET_DEFAULT: int = 0

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_COOKIE_NAME: str = "access_token"
    JWT_SECRET_KEY: str
    ENCODE_ALGORITHM: str
    DECODE_ALGORITHMS: List[str]

    PASSWORD_MIN_LENGTH: int = 8
