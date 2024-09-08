from typing import Annotated, List

from app.common.dependencies.filters_input.base import BaseFiltersInput
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Bookings
from fastapi import Depends, Query
from pydantic import Field

columns = get_columns_by_table(Bookings)
BookingsOrderingEnum = get_ordering_enum_by_columns(
    "BookingsOrderingEnum", columns.price, columns.date_from, columns.date_to
)


class BookingsFiltersInput(BaseFiltersInput):
    room_id: int | None = None
    ordering: List[BookingsOrderingEnum] | None = Field(Query(None))


BookingsFiltersDep = Annotated[BookingsFiltersInput, Depends(BookingsFiltersInput)]
