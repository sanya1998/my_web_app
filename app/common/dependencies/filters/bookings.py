from typing import Annotated, List

from app.common.dependencies.filters.base import BaseFiltersSchema
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Bookings
from fastapi import Depends, Query
from pydantic import Field, computed_field
from pydantic.json_schema import SkipJsonSchema

columns = get_columns_by_table(Bookings)
BookingsOrderingEnum = get_ordering_enum_by_columns(columns.price, columns.date_from, columns.date_to)


class BookingsBaseFiltersSchema(BaseFiltersSchema):
    room_id: int | None = None
    price_min: int | None = None
    price_max: int | None = None
    ordering: List[BookingsOrderingEnum] | None = Field(Query(None))

    @computed_field
    @property
    def price(self) -> tuple[int | None, int | None] | None:
        return (self.price_min, self.price_max) if self.price_min or self.price_max else None


BookingsFiltersDep = Annotated[BookingsBaseFiltersSchema, Depends(BookingsBaseFiltersSchema)]
