import click
from app.config.common import settings
from app.resources.hawk_ import init_hawk
from app.resources.sentry_ import init_sentry

init_sentry()
init_hawk()


@click.group()
def cli() -> None:
    pass


@cli.command()
def runserver() -> None:
    """Run the server."""
    import uvicorn
    from app.app import app

    uvicorn.run(app=app, host=settings.API_HOST, port=settings.API_PORT)


# TODO:
@cli.command()
def runserver_hypercorn() -> None:
    """Run the server with Hypercorn (better HTTP/2 support)."""
    import asyncio

    from app.app import app
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = [f"{settings.API_HOST}:{settings.API_PORT}"]
    config.certfile = getattr(settings, "SSL_CERTFILE", None)
    config.keyfile = getattr(settings, "SSL_KEYFILE", None)

    # Явно включаем HTTP/2
    config.http2 = True  # Пока браузер пишет, что все равно http/1.1

    # Дополнительные настройки для лучшей поддержки HTTP/2
    config.worker_class = "asyncio"

    click.echo(f"Starting server with HTTP/2 support on https://{settings.API_HOST}:{settings.API_PORT}")
    asyncio.run(serve(app, config))


@cli.command()
def run_history_consumer() -> None:
    """Run consumer of history of queries."""
    import asyncio

    from app.consumers.history import HistoryConsumer

    consumer = HistoryConsumer(queue_name=settings.HISTORY_QUEUE_NAME)
    asyncio.run(consumer.blocking_consume())


@cli.command()
def run_es_write_consumer() -> None:
    """Run consumer of es_write_consumer."""
    import asyncio

    from app.consumers.es_write import ESWriteConsumer

    consumer = ESWriteConsumer(queue_name=settings.ES_WRITE_QUEUE_NAME, use_write_alias=False)
    asyncio.run(consumer.blocking_consume())


@cli.command()
def run_es_write_reindex_consumer() -> None:
    """Run consumer of es_write_consumer for reindex."""
    import asyncio

    from app.consumers.es_write import ESWriteConsumer

    consumer = ESWriteConsumer(queue_name=settings.ES_WRITE_REINDEX_QUEUE_NAME, use_write_alias=True)
    asyncio.run(consumer.blocking_consume())


if __name__ == "__main__":
    cli()
