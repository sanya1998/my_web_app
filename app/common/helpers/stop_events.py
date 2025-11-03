import asyncio
import signal


def configure_event_of_stop_signal() -> asyncio.Event:
    """Инициализация stop_event и регистрация обработчиков сигналов"""
    signals = (
        signal.SIGINT,  # ctrl+c из терминала
        signal.SIGTERM,  # Сигнал завершения от системы (kill)
        signal.SIGQUIT,  # ctrl+\ из терминала (создает core dump)
    )
    loop = asyncio.get_running_loop()
    event = asyncio.Event()
    for sig in signals:
        loop.add_signal_handler(sig, event.set)
    return event
