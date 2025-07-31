from datetime import datetime
from zoneinfo import ZoneInfo

from app.common.schemas.base import BaseSchema
from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo


class IdMixin(BaseSchema):
    id: int


class CreatedMixin(BaseSchema):
    created_dt: datetime


class UpdatedMixin(BaseSchema):
    updated_dt: datetime


class IdCreatedUpdatedMixin(IdMixin, CreatedMixin, UpdatedMixin):
    @field_validator("created_dt", "updated_dt", mode="after")
    @classmethod
    def replace_dt(cls, dt: datetime, info: ValidationInfo):
        new_timezone = "Europe/Moscow"
        dt_moscow = dt.astimezone(ZoneInfo(new_timezone))
        # dt_moscow_without_tz = dt_moscow.replace(tzinfo=None)
        return dt_moscow
