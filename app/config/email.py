from pydantic_settings import BaseSettings


class EmailSettings(BaseSettings):
    """
    Конфигурация email
    """

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str
    SMTP_PASSWORD: str
