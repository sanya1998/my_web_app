import click
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
    from app.config.common import settings

    uvicorn.run(app=app, host=settings.HOST, port=settings.PORT)


if __name__ == "__main__":
    cli()
