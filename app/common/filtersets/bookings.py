from app.common.filtersets.base import BaseCustomFilterSet
from app.common.tables import Bookings
from sqlalchemy.sql import operators as ops
from sqlalchemy_filterset import Filter, NullsPosition, OrderingField, OrderingFilter, RangeFilter


class BookingsFilterSet(BaseCustomFilterSet):
    user_id = Filter(Bookings.user_id, lookup_expr=ops.eq)
    room_id = Filter(Bookings.room_id, lookup_expr=ops.eq)
    price = RangeFilter(Bookings.price, left_lookup_expr=ops.ge, right_lookup_expr=ops.le)
    ordering = OrderingFilter(
        price=OrderingField(Bookings.price),
        date_from=OrderingField(Bookings.date_from, nulls=NullsPosition.last),
        date_to=OrderingField(Bookings.date_to, nulls=NullsPosition.last),
    )
