from typing import Annotated, List, Tuple

from app.common.dependencies.filters.base import MainFilters, filter_depends
from app.common.dependencies.filters.common.rooms import RoomBaseFilters
from app.common.dependencies.filters.common.users import UserBaseFilter
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Bookings
from fastapi import Query
from pydantic import Field

columns = get_columns_by_table(Bookings)
BookingsOrderingEnum = get_ordering_enum_by_columns(
    "BookingsOrderingEnum", columns.price, columns.date_from, columns.date_to
)


class BookingsFilters(MainFilters):
    _db_model = Bookings
    room_id: int | None = None
    room: RoomBaseFilters
    total_cost__between: Annotated[Tuple[int, int] | None, Field(Query(None))]
    order_by: Annotated[List[BookingsOrderingEnum] | None, Field(Query(None))]
    user: UserBaseFilter


BookingsFiltersDep = Annotated[BookingsFilters, filter_depends(BookingsFilters)]
