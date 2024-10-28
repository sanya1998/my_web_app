from pydantic_settings import BaseSettings


class CelerySettings(BaseSettings):
    """
    Конфигурация брокера celery
    """

    CELERY_BROKER_URL: str
    CELERY_BROKER_HOST: str
    CELERY_BROKER_PORT: int
