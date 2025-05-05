from app.config.common import settings
from pydantic import Field

PASSWORD_FIELD = Field(min_length=settings.PASSWORD_MIN_LENGTH)
