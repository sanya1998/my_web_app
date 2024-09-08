from datetime import date

from pydantic import BaseModel, computed_field


class DatesFiltersInput(BaseModel):
    date_from: date | None = None
    date_to: date | None = None

    @computed_field
    @property
    def dates(self) -> tuple[date, date] | None:
        return (self.date_from, self.date_to) if self.date_from and self.date_to else None
