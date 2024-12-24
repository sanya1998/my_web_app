from datetime import date
from typing import List

from app.common.dependencies.parameters.base import (
    CustomFilter,
    CustomSort,
    create_depends,
)
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Rooms
from fastapi import Query
from pydantic import Field


class BaseRoomsFilter(CustomFilter):
    price__gt: int
    price__lt: int
    check_into: date
    check_out: date


columns = get_columns_by_table(Rooms)
RoomsOrderingEnum = get_ordering_enum_by_columns("RoomsOrderingEnum", columns.price)


class RoomsFilter(BaseRoomsFilter):
    hotel_id: int | None = None  # TODO: check


class RoomsSorts(CustomSort):
    ordering: List[RoomsOrderingEnum] | None = Field(Query(None))


RoomsParametersDep = create_depends(filters_class=RoomsFilter, sorts_class=RoomsSorts)
