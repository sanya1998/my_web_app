import click


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
    from app.config import settings

    uvicorn.run(app=app, host=settings.DB_HOST, port=settings.DB_PORT)


if __name__ == "__main__":
    cli()
