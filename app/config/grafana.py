from pydantic_settings import BaseSettings


class GrafanaSettings(BaseSettings):
    """
    Настройки grafana
    """

    GRAFANA_VERSION: str
    GRAFANA_PORT: int
    GF_SECURITY_ADMIN_USER: str
    GF_SECURITY_ADMIN_PASSWORD: str
