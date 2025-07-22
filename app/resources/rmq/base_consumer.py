import asyncio
import functools
import pickle
import signal

from aio_pika import IncomingMessage
from app.common.logger import logger
from app.config.common import settings
from app.resources.rmq.base import BaseRabbitMQ


class BaseConsumer(BaseRabbitMQ):
    def __init__(self, queue_name: str = "", **kwargs):
        self.queue_name = queue_name
        super().__init__(**kwargs)

    @staticmethod
    async def process_message(message: IncomingMessage):
        # TODO: некоторые используют JsonSerializer, провести замеры производительности, памяти
        # TODO: попробовать взломать самого себя: отправить в этот консьюмер объект, реализовать в нем хакерский getter
        message = pickle.loads(message.body)
        return message

    async def __consume(
        self,
        prefetch_count=settings.RMQ_PREFETCH_COUNT_DEFAULT,
    ):
        await self.channel.set_qos(prefetch_count=prefetch_count)
        queue = await self.channel.get_queue(name=self.queue_name)

        async with queue.iterator() as queue_iter:
            logger.info(f"Consuming queue {self.queue_name}")
            async for message in queue_iter:
                message: IncomingMessage
                try:
                    await self.process_message(message)
                except Exception as e:
                    logger.error(f"Exception while processing message: {message}. Exc: {e}")
                else:
                    await message.ack()

    def setup_exiting(self):
        """
        При прерывании консюмера не выполняется __aexit__, поэтому необходима эта настройка
        """
        callback = functools.partial(asyncio.create_task, self.shutdown())
        asyncio.get_running_loop().add_signal_handler(signal.SIGINT, callback)

    async def consume(self, *args, **kwargs):
        self.setup_exiting()
        async with self:
            await self.__consume(*args, **kwargs)
