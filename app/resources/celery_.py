import sentry_sdk
from app.config.common import settings
from celery import Celery, signals

celery = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    include=[
        "app.tasks.img",
        "app.tasks.email",
    ],
)
celery.conf.broker_connection_retry_on_startup = True


# TODO: Если celery будет запускаться из manage.py, то возможно, что нужна будет только одна инициализация sentry
@signals.celeryd_init.connect
def init_sentry_for_celery(**_kwargs):
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=settings.RELEASE_VERSION,
        # TODO: check
        # integrations=[
        #     CeleryIntegration(
        #         monitor_beat_tasks=True,
        #         exclude_beat_tasks=[
        #             "unimportant-task",
        #             "payment-check-.*"
        #         ],
        #     ),
        # ],
    )
