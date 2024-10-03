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
    from app.config.main import settings

    uvicorn.run(app="app.app:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)


if __name__ == "__main__":
    cli()
