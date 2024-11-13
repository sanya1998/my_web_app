from datetime import date

from app.common.constants.datetimes import TODAY, TOMORROW
from app.common.exceptions.api.unprocessable_entity import UnprocessableEntityApiError
from fastapi import Query
from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import ValidationInfo


class DatesFiltersInput(BaseModel):
    date_from: date | None = Field(Query(None, description=f"Example: {TODAY}"))
    date_to: date | None = Field(Query(None, description=f"Example: {TOMORROW}"))
    dates: tuple[date, date] | None = Field(Query(None, include_in_schema=False))

    @field_validator("dates")
    @classmethod
    def validate_dates(cls, dates: None, info: ValidationInfo) -> tuple[date, date] | None:
        if not (date_from := info.data["date_from"]) or not (date_to := info.data["date_to"]):
            return None
        days = (date_to - date_from).days
        if days <= 0 or days > 30:
            raise UnprocessableEntityApiError(detail="Invalid dates. Must be between 1 and 30 days.")
        return date_from, date_to
