from app.config.common import settings
from fastapi import Body

PASSWORD_BODY = Body(min_length=settings.PASSWORD_MIN_LENGTH)
