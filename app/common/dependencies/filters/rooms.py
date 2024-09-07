from typing import Annotated, List

from app.common.dependencies.filters.base import BaseFiltersSchema
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Rooms
from fastapi import Depends, Query
from pydantic import Field, computed_field

columns = get_columns_by_table(Rooms)
RoomsOrderingEnum = get_ordering_enum_by_columns("RoomsOrderingEnum", columns.price)


class RoomsBaseFiltersSchema(BaseFiltersSchema):
    price_min: int | None = None
    price_max: int | None = None
    ordering: List[RoomsOrderingEnum] | None = Field(Query(None))

    @computed_field
    @property
    def price(self) -> tuple[int | None, int | None] | None:
        return (self.price_min, self.price_max) if self.price_min or self.price_max else None


RoomsFiltersDep = Annotated[RoomsBaseFiltersSchema, Depends(RoomsBaseFiltersSchema)]
