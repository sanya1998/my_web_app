from datetime import date

from app.common.constants.datetimes import TODAY, TOMORROW
from fastapi import Query
from pydantic import BaseModel, Field, computed_field


class DatesFiltersInput(BaseModel):
    date_from: date | None = Field(Query(None, description=f"Example: {TODAY}"))
    date_to: date | None = Field(Query(None, description=f"Example: {TOMORROW}"))

    @computed_field
    @property
    def dates(self) -> tuple[date, date] | None:
        return (self.date_from, self.date_to) if self.date_from and self.date_to else None
