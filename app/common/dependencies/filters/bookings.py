from typing import List, Tuple

from app.common.constants.roles import BookingsRecipientRoleEnum
from app.common.dependencies.filters.base import MainFilters, get_depends_by_filters_model
from app.common.dependencies.filters.common import RoomBaseFilters, UserBaseFilters
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Bookings
from pydantic import field_validator

columns = get_columns_by_table(Bookings)
BookingsOrderingEnum = get_ordering_enum_by_columns(
    "BookingsOrderingEnum", columns.price, columns.date_from, columns.date_to
)


class BookingsFilters(MainFilters):
    _db_model = Bookings

    room_id: int | None = None
    room: RoomBaseFilters
    total_cost__between: Tuple[int, int] | None = None
    order_by: List[BookingsOrderingEnum] | None = None
    user: UserBaseFilters

    # Проверка возможности валидации поля в BaseFilters (TODO: удалить)
    @field_validator("room_id", mode="before")
    def check(cls, value: str | None) -> str | int:
        if value and (value := int(value)) < 0:
            return abs(value)
        return value


class BookingsQueryParams(BookingsFilters):
    recipient_role: BookingsRecipientRoleEnum


BookingsQueryParamsDep = get_depends_by_filters_model(BookingsQueryParams)
