from pydantic_settings import BaseSettings


class CelerySettings(BaseSettings):
    """
    Конфигурация брокера celery
    """

    CELERY_BROKER_URL: str
    #
    # CELERY_WORKER_HOST: str  # TODO: связать
    # CELERY_WORKER_PORT: int  # TODO: связать
    #
    # CELERY_FLOWER_HOST: str  # TODO: связать
    # CELERY_FLOWER_PORT: int  # TODO: связать
