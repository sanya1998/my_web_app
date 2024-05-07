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