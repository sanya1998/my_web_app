from typing import List

from app.common.dependencies.parameters.base import (
    CustomFilter,
    CustomSort,
    create_depends,
)
from app.common.dependencies.parameters.rooms import BaseRoomsFilter
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Hotels
from fastapi import Query
from pydantic import Field
from pydantic_filters import FilterField, SearchField

columns = get_columns_by_table(Hotels)
HotelsOrderingEnum = get_ordering_enum_by_columns("HotelsOrderingEnum", columns.id, columns.name, columns.location)


class HotelsSorts(CustomSort):
    ordering: List[HotelsOrderingEnum] | None = Field(Query([HotelsOrderingEnum.ID]))


class HotelsFilters(CustomFilter):
    name: str = SearchField(target=[columns.name.name])
    location: str = FilterField(type_="ilike")
    rooms: BaseRoomsFilter

    # TODO:
    # PricesFiltersSet, DatesFiltersSet
    #     # has_spa
    #     # stars


HotelsParametersDep = create_depends(filters_class=HotelsFilters, sorts_class=HotelsSorts)
