from typing import Annotated, List

from app.common.dependencies.filters_input.base import BaseFiltersInput
from app.common.dependencies.filters_input.custom.dates import DatesFiltersInput
from app.common.dependencies.filters_input.custom.prices import PricesFiltersInput
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Rooms
from fastapi import Depends, Query
from pydantic import Field

columns = get_columns_by_table(Rooms)
RoomsOrderingEnum = get_ordering_enum_by_columns("RoomsOrderingEnum", columns.price)


class RoomsFiltersInput(BaseFiltersInput, PricesFiltersInput, DatesFiltersInput):
    hotel_id: int | None = None
    ordering: List[RoomsOrderingEnum] | None = Field(Query(None))


RoomsFiltersDep = Annotated[RoomsFiltersInput, Depends(RoomsFiltersInput)]
