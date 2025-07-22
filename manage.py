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
    """
    Run the server.
    """
    import uvicorn
    from app.app import app

    uvicorn.run(app=app, host=settings.API_HOST, port=settings.API_PORT)
    # TODO: http2
    # import asyncio
    # from hypercorn.config import Config
    # from hypercorn.asyncio import serve
    #
    # asyncio.run(serve(app, Config()))


@cli.command()
def run_history_consumer() -> None:
    """
    Run consumer of history of queries.
    """
    import asyncio

    from app.consumers.history import HistoryConsumer

    consumer = HistoryConsumer(queue_name=settings.HISTORY_QUEUE_NAME)
    asyncio.run(consumer.consume())


if __name__ == "__main__":
    cli()
