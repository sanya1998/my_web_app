from typing import List

from app.common.dependencies.filters.base import MainFilters, get_depends_by_filters_model
from app.common.dependencies.filters.common import RoomBaseFilters, RoomsBaseFilters
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Rooms

columns = get_columns_by_table(Rooms)
RoomsOrderingEnum = get_ordering_enum_by_columns("RoomsOrderingEnum", columns.price, columns.id)


class RoomsFilters(MainFilters, RoomBaseFilters, RoomsBaseFilters):
    order_by: List[RoomsOrderingEnum] | None = None


RoomsFiltersDep = get_depends_by_filters_model(RoomsFilters)
