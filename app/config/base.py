from os.path import dirname

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Базовые настройки приложения
    """

    APPLICATION_NAME: str = "My web application"
    APPLICATION_DESCRIPTION: str = "My web application description"

    #: Режим отладки
    DEBUG: bool = True

    #: Порт
    PORT: int = 8000

    #: Хост
    HOST: str = "0.0.0.0"


settings = Settings()
