import asyncio
import logging
from typing import Set

from starlette.requests import Request

logger = logging.getLogger(__name__)

# TODO:
# Redis Pub/Sub архитектура
# Клиент1 → Redis Channel ──▶ Клиент1
# Клиент2 → Redis Channel ──▶ Клиент2
# Клиент3 → Redis Channel ──▶ Клиент3
#          (автоматическая рассылка)

# Текущая архитектура (asyncio.Queue)
# Клиент1 → Queue1 ──┐
# Клиент2 → Queue2 ──┤─ SSEManager → Рассылка вручную
# Клиент3 → Queue3 ──┘
# Работает только с 2 sse-клиентами, на 3 sse-клиенте почему-то блокируется все приложение


class SSEManager:
    def __init__(self):
        self.connections: Set[asyncio.Queue] = set()

    async def create_connection(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self.connections.add(queue)
        logger.info(f"New SSE connection. Total: {len(self.connections)}")
        return queue

    async def remove_connection(self, queue: asyncio.Queue):
        self.connections.discard(queue)
        logger.info(f"SSE connection removed. Total: {len(self.connections)}.")

    async def send_message(self, message: str, batch_size: int = 1000):
        if not self.connections:
            return

        connections_list = list(self.connections)

        # Благодаря разделению на батчи можно иметь большее число клиентов.
        for i in range(0, len(connections_list), batch_size):
            batch = connections_list[i : i + batch_size]
            tasks = [asyncio.create_task(queue.put(message)) for queue in batch]
            await asyncio.gather(*tasks, return_exceptions=True)

        logger.info(f"Message sent to {len(self.connections)} clients.")

    async def event_generator(self, request: Request):
        """Генератор событий"""
        queue = await self.create_connection()
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield message
                except asyncio.TimeoutError:
                    continue
        finally:
            await self.remove_connection(queue)
