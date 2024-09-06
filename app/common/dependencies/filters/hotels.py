from typing import Annotated, List

from app.common.dependencies.filters.base import BaseFiltersSchema
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Hotels
from fastapi import Depends, Query
from pydantic import Field
from pydantic.json_schema import SkipJsonSchema

columns = get_columns_by_table(Hotels)
HotelsOrderingEnum = get_ordering_enum_by_columns(columns.name, columns.location)


class HotelsBaseFiltersSchema(BaseFiltersSchema):
    location: str | None = None
    ordering: List[HotelsOrderingEnum] | None = Field(Query(None))

    # TODO:
    # price_min: int | None = None
    # price_max: int | None = None
    # date_from
    # date_to
    # has_spa
    # stars


HotelsFiltersDep = Annotated[HotelsBaseFiltersSchema, Depends(HotelsBaseFiltersSchema)]
