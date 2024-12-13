from pydantic import computed_field
from pydantic_settings import BaseSettings


class DbSettings(BaseSettings):
    """
    Конфигурация баз данных
    """

    # REDIS
    REDIS_VERSION: str
    REDIS_DRIVER: str = "redis"
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USER: str
    REDIS_PASSWORD: str
    REDIS_DB: str
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_CACHE_EXPIRE_DEFAULT: int = 120
    REDIS_CACHE_EXPIRE_HOTELS: int = 60

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        value = (
            f"{self.REDIS_DRIVER}://"
            f"{self.REDIS_USER}:{self.REDIS_PASSWORD}@"
            f"{self.REDIS_HOST}:{self.REDIS_PORT}/"
            f"{self.REDIS_DB}"
        )
        return value

    # POSTGRES
    POSTGRES_VERSION: str
    POSTGRES_DRIVER: str = "postgresql+asyncpg"
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # DB_WRITE_MIN_POOL_SIZE: int = 4
    # DB_WRITE_MAX_POOL_SIZE: int = 10
    # DB_READ_MIN_POOL_SIZE: int = 5
    # DB_READ_MAX_POOL_SIZE: int = 20
    # DB_COMMAND_TIMEOUT: float = 10.0

    @computed_field
    @property
    def POSTGRES_URL(self) -> str:
        value = (
            f"{self.POSTGRES_DRIVER}://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )
        return value
