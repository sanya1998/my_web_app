from app.config.main import settings
from fastapi import Form
from pydantic import Field

PASSWORD_FIELD = Field(Form(min_length=settings.PASSWORD_MIN_LENGTH))
