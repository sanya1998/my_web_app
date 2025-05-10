from datetime import date
from typing import Annotated

from app.common.constants.datetimes import TODAY, TOMORROW
from app.common.dependencies.filters.base import BaseFilters
from app.common.dependencies.filters.common import HotelBaseFilters
from app.common.exceptions.api import UnprocessableEntityApiError
from app.common.tables import Rooms
from pydantic import Field, model_validator
from typing_extensions import Self


class BaseBaseFilters(BaseFilters):
    _db_model = Rooms


class RoomBaseFilters(BaseBaseFilters):
    name: str | None = None
    hotel_id: int | None = None
    hotel: HotelBaseFilters


class RoomsBaseFilters(BaseBaseFilters):
    price__gt: int | None = None
    price__lt: int | None = None
    check_into: Annotated[date | None, Field(description=f"Example: {TODAY}")] = None
    check_out: Annotated[date | None, Field(description=f"Example: {TOMORROW}")] = None

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.check_into and self.check_out:
            days = (self.check_out - self.check_into).days
            if days <= 0 or days > 30:
                raise UnprocessableEntityApiError(detail="Invalid dates. Must be between 1 and 30 days.")
        return self
