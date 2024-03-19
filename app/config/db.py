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

    DB_WRITE_MIN_POOL_SIZE: int = 4
    DB_WRITE_MAX_POOL_SIZE: int = 10

    DB_READ_MIN_POOL_SIZE: int = 5
    DB_READ_MAX_POOL_SIZE: int = 20

    DB_COMMAND_TIMEOUT: float = 10.0


db_settings = DbSettings()
