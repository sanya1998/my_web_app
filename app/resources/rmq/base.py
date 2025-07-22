from aio_pika import RobustChannel, connect_robust
from aio_pika.abc import AbstractRobustConnection, ExchangeType
from app.config.common import settings


class BaseRabbitMQ:
    def __init__(self, *args, **kwargs):
        self.connection: AbstractRobustConnection | None = None
        self.channel: RobustChannel | None = None

    async def set_connection(self):
        self.connection = await connect_robust(
            host=settings.RMQ_HOST,
            port=settings.RMQ_PORT,
            login=settings.RABBITMQ_DEFAULT_USER,
            password=settings.RABBITMQ_DEFAULT_PASS,
            virtualhost=settings.RABBITMQ_DEFAULT_VHOST,
        )
        return self.connection

    async def set_channel(self):
        self.channel = await self.connection.channel()
        return self.channel

    async def setup(self):
        await self.set_connection()
        await self.set_channel()

    async def __aenter__(self):
        await self.setup()
        return self

    async def shutdown(self):
        if not self.channel.is_closed:
            await self.channel.close()
        if not self.connection.is_closed:
            await self.connection.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()

    async def bind(
        self,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
        exchange_type: ExchangeType = ExchangeType.DIRECT,
        durable: bool = settings.RMQ_DURABLE_DEFAULT,
    ):
        exchange = await self.channel.declare_exchange(exchange_name, exchange_type, durable=durable)
        queue = await self.channel.declare_queue(queue_name, durable=durable)
        await queue.bind(exchange, routing_key)

    @staticmethod
    def with_channel(method):
        """Использование одного соединения и нескольких каналов"""

        async def wrapper(self, *args, **kwargs):
            channel = await self.connection.channel()
            try:
                return await method(self, *args, channel=channel, **kwargs)
            finally:
                await channel.close()

        return wrapper
