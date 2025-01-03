from typing import Annotated, List

from app.common.dependencies.filters.base import MainFilters, filter_depends
from app.common.dependencies.filters.common.rooms import RoomBaseFilters, RoomsBaseFilters
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Rooms
from fastapi import Query
from pydantic import Field

columns = get_columns_by_table(Rooms)
RoomsOrderingEnum = get_ordering_enum_by_columns("RoomsOrderingEnum", columns.price, columns.id)


class RoomsFilters(MainFilters, RoomBaseFilters, RoomsBaseFilters):
    order_by: List[RoomsOrderingEnum] | None = Field(Query(None))


RoomsFiltersDep = Annotated[RoomsFilters, filter_depends(RoomsFilters)]
