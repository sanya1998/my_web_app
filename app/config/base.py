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

    #: Хост
    HOST: str = "localhost"
    #: Порт
    PORT: int = 8000


settings = Settings()
