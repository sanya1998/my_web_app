from pydantic import computed_field
from pydantic_settings import BaseSettings


class DbSettings(BaseSettings):
    """
    Конфигурация баз данных
    """

    # TODO: разбить по дочерним классам разные бд

    # REDIS
    REDIS_VERSION: str
    REDIS_DRIVER: str = "redis"  # TODO: или DIALECT, а не DRIVER?
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USER: str
    REDIS_PASSWORD: str

    CACHE_DB: int
    CACHE_MAX_CONNECTIONS: int = 10
    CACHE_EXPIRE_DEFAULT: int = 120
    CACHE_EXPIRE_HOTELS: int = 60

    @computed_field
    @property
    def REDIS_BASE_URL(self) -> str:
        value = (
            f"{self.REDIS_DRIVER}://" f"{self.REDIS_USER}:{self.REDIS_PASSWORD}@" f"{self.REDIS_HOST}:{self.REDIS_PORT}"
        )
        return value

    # TODO: use REDIS_BASE_URL
    @computed_field
    @property
    def CACHE_URL(self) -> str:
        value = (
            f"{self.REDIS_DRIVER}://"
            f"{self.REDIS_USER}:{self.REDIS_PASSWORD}@"
            f"{self.REDIS_HOST}:{self.REDIS_PORT}/"
            f"{self.CACHE_DB}"
        )
        return value

    CELERY_BROKER_DB: int
    FLOWER_PORT: int

    # TODO: use REDIS_BASE_URL
    @computed_field
    @property
    def CELERY_BROKER_URL(self) -> str:
        value = (
            f"{self.REDIS_DRIVER}://"
            f"{self.REDIS_USER}:{self.REDIS_PASSWORD}@"
            f"{self.REDIS_HOST}:{self.REDIS_PORT}/"
            f"{self.CELERY_BROKER_DB}"
        )
        return value

    # POSTGRES
    POSTGRES_VERSION: str
    POSTGRES_DIALECT: str = "postgresql"
    POSTGRES_DRIVER: str = "asyncpg"
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # размер пула соединений
    DB_POOL_SIZE: int = 20
    # Если соединений не хватает, то можно создать на время дополнительные
    DB_MAX_OVERFLOW: int = 10

    # TODO: хорошая практика - разделить пулы на запись и чтение
    # DB_WRITE_MIN_POOL_SIZE: int = 4
    # DB_WRITE_MAX_POOL_SIZE: int = 10
    # DB_READ_MIN_POOL_SIZE: int = 5
    # DB_READ_MAX_POOL_SIZE: int = 20

    # Время жизни соединения в пуле. Если оно не используется указанное время (в секундах), то будет заменено на новое
    DB_POOL_RECYCLE: int = 600
    # Перед использованием соединения происходит пинг БД (SELECT 1), если соединение не работает, будет переподключение
    DB_POOL_PRE_PING: bool = True

    @computed_field
    @property
    def POSTGRES_URL(self) -> str:
        value = (
            f"{self.POSTGRES_DIALECT}+{self.POSTGRES_DRIVER}://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )
        return value

    FILE_FORMAT: str = "csv"
    FILE_ENCODING: str = "utf-8"
    FILE_MEDIA_TYPE: str = "text/csv"

    PROMETHEUS_VERSION: str
    PROMETHEUS_PORT: int
