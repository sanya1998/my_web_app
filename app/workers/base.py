import asyncio
from typing import Optional

from app.common.helpers.stop_events import configure_event_of_stop_signal
from app.common.logger import logger


class BaseWorker:
    """
    Patterns:
    class Worker(BaseWorker):
        async def work(self):
            pass

    # 1 blocking worker
    asyncio.run(worker.blocking_start())

    # 2 async worker
    async with Worker(interval=60) as worker:
        await worker.start()
        # Stop, for example: `await asyncio.Future()`
        # Stop, for another example in FastApi lifespan: 'yield'
    """

    def __init__(self, interval: float, name: Optional[str] = None):
        self.interval = interval
        self.name = name or self.__class__.__name__
        self.stop_event: Optional[asyncio.Event] = None
        self._task: Optional[asyncio.Task] = None

    async def work(self) -> None:
        """Основная работа воркера. Переопределяется в дочерних классах."""
        raise NotImplementedError

    async def _safe_work(self) -> None:
        try:
            await self.work()
        except Exception as e:
            logger.error(f"Worker {self.name}: work failed: {e}")

    async def _safe_timeout(self) -> None:
        """Ждать либо заданный интервал, либо сигнал остановки"""
        try:
            await asyncio.wait_for(self.stop_event.wait(), timeout=self.interval)
        except asyncio.TimeoutError:
            pass

    async def _run_worker(self) -> None:
        """Внутренний метод для запуска воркера"""
        while not self.stop_event.is_set():
            await self._safe_work()
            await self._safe_timeout()

    async def start(self) -> None:
        """Асинхронный запуск (работает в фоне)"""
        logger.info(f"Worker {self.name}: async start with interval {self.interval}s.")
        if self._task and not self._task.done():
            logger.warning(f"Worker {self.name}: already running.")
            return

        self._task = asyncio.create_task(self._run_worker(), name=f"worker_{self.name}.")

    async def blocking_start(self) -> None:
        """Блокирующий запуск (работает до сигнала остановки)"""
        self.stop_event = configure_event_of_stop_signal()
        logger.info(f"Worker {self.name}: blocking start with interval {self.interval}s")
        logger.info("[*] To exit press CTRL+C")
        await self._run_worker()
        logger.info(f"Worker {self.name}: stopped")

    async def setup(self) -> None:
        """Асинхронная инициализация ресурсов"""
        pass

    async def __aenter__(self):
        await self.setup()
        return self

    async def stop(self) -> None:
        """Остановка воркера"""
        # 1. Установка флага остановки
        if self.stop_event:
            self.stop_event.set()

        # 2. Ждем завершения задачи
        if self._task:
            try:
                await self._task  # Задача завершится на следующей проверке stop_event
            except asyncio.CancelledError:
                pass  # Если задача уже была отменена извне
            finally:
                self._task = None

        logger.info(f"Worker {self.name}: stopped")

    async def shutdown(self) -> None:
        """Асинхронное освобождение ресурсов"""
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
        await self.shutdown()

    @property
    def is_running(self) -> bool:
        """Проверка, запущен ли воркер"""
        return self._task is not None and not self._task.done()


class SimpleWorker(BaseWorker):
    async def work(self) -> None:
        from datetime import datetime

        logger.info(f"{self.name}: {datetime.now()}")


async def main() -> None:
    # Вариант 1: Blocking worker
    await SimpleWorker(2, "BLOCKING").blocking_start()

    # Вариант 2: Async worker с таймаутом
    # async with SimpleWorker(2) as worker:
    #     await worker.start()
    #     await asyncio.sleep(10)

    # Вариант 3: Async worker с сигналом остановки
    # async with SimpleWorker(2, "ASYNC1") as w1, SimpleWorker(2, "ASYNC2") as w2:
    #     await asyncio.gather(w1.start(), w2.start())
    #     await asyncio.Future()

    # Вариант 4: Смешанный вариант
    # async with SimpleWorker(2, "ASYNC1") as w1, SimpleWorker(2, "ASYNC2") as w2:
    #     await asyncio.gather(w1.start(), w2.start())
    #     await SimpleWorker(2, "BLOCKING").blocking_start()


if __name__ == "__main__":
    asyncio.run(main())
