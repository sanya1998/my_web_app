from typing import Annotated

from app.common.dependencies.filters.base import BaseFilterSchema, _BaseFilterSet
from app.common.tables import Bookings
from fastapi import Depends
from pydantic import computed_field
from sqlalchemy.sql import operators as ops
from sqlalchemy_filterset import Filter, RangeFilter


class BookingsFilterSet(_BaseFilterSet):
    user_id = Filter(Bookings.user_id, lookup_expr=ops.eq)
    room_id = Filter(Bookings.room_id, lookup_expr=ops.eq)
    price = RangeFilter(
        Bookings.price,
        left_lookup_expr=ops.ge,
        right_lookup_expr=ops.le,
        logic_expr=ops.and_,
    )
    # date_from: date = "2023-06-15"
    # bb: int = 3
    # date_to: date


class BookingsFilterSchema(BaseFilterSchema):
    room_id: int | None = None
    user_id: int | None = None
    price_min: int | None = None
    price_max: int | None = None

    @computed_field
    @property
    def price(self) -> tuple[int | None, int | None]:
        return self.price_min, self.price_max


BookingsFiltersDep = Annotated[BookingsFilterSchema, Depends(BookingsFilterSchema)]
