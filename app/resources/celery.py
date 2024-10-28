from app.config.main import settings
from celery import Celery

celery = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    include=["app.common.tasks.img"],
)
celery.conf.broker_connection_retry_on_startup = True
