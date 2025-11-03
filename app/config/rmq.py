from pydantic_settings import BaseSettings


class RabbitMQSettings(BaseSettings):
    """
    Конфигурация rabbitmq
    """

    RMQ_VERSION: str
    RMQ_HOST: str
    RMQ_PORT: int
    RMQ_GUI_PORT: int
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_DEFAULT_VHOST: str
    RMQ_PREFETCH_COUNT_DEFAULT: int = 10
    RMQ_DURABLE_DEFAULT: bool = True

    HISTORY_ROUTING_KEY: str = "history_routing_key"
    HISTORY_QUEUE_NAME: str = "history_queue"
    HISTORY_EXCHANGE_NAME: str = "history_exchange"

    SSE_ROUTING_KEY: str = "sse_routing_key"
    SSE_QUEUE_NAME: str = "sse_queue"
    SSE_EXCHANGE_NAME: str = "sse_exchange"
