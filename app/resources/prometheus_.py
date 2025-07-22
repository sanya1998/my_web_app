from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/admin/*", "/metrics"],
)


def add_prometheus(app: FastAPI) -> None:
    instrumentator.instrument(app).expose(app)
    # TODO: не нужно ли PrometheusMiddleware ?
