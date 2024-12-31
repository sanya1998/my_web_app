from typing import Annotated, List

from app.common.dependencies.filters.base import MainFilters, filter_depends
from app.common.dependencies.filters.common.hotels import HotelBaseFilters
from app.common.dependencies.filters.common.rooms import RoomsBaseFilters
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Hotels
from fastapi import Query
from pydantic import Field

columns = get_columns_by_table(Hotels)
HotelsOrderingEnum = get_ordering_enum_by_columns("HotelsOrderingEnum", columns.id, columns.name, columns.location)


class HotelsFilters(MainFilters, HotelBaseFilters):
    location__ilike: str | None = None  # TODO: show sql-query
    order_by: List[HotelsOrderingEnum] | None = Field(Query([HotelsOrderingEnum.ID]))
    rooms: RoomsBaseFilters

    # TODO:
    # has_spa
    # stars


HotelsFiltersDep = Annotated[HotelsFilters, filter_depends(HotelsFilters)]
