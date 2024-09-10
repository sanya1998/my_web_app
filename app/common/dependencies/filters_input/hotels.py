from typing import Annotated, List

from app.common.dependencies.filters_input.base import BaseFiltersInput
from app.common.dependencies.filters_input.custom.dates import DatesFiltersInput
from app.common.dependencies.filters_input.custom.prices import PricesFiltersInput
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Hotels
from fastapi import Depends, Query
from pydantic import Field

columns = get_columns_by_table(Hotels)
HotelsOrderingEnum = get_ordering_enum_by_columns("HotelsOrderingEnum", columns.name, columns.location)


class HotelsFiltersInput(BaseFiltersInput, PricesFiltersInput, DatesFiltersInput):
    location: str | None = None
    ordering: List[HotelsOrderingEnum] | None = Field(Query(None))

    # TODO:
    # has_spa
    # stars


HotelsFiltersDep = Annotated[HotelsFiltersInput, Depends(HotelsFiltersInput)]
