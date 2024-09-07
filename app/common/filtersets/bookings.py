from app.common.filtersets.base import BaseFiltersSet
from app.common.tables import Bookings
from sqlalchemy.sql.operators import eq
from sqlalchemy_filterset import Filter, NullsPosition, OrderingField, OrderingFilter


class BookingsFiltersSet(BaseFiltersSet):
    user_id = Filter(Bookings.user_id, lookup_expr=eq)
    room_id = Filter(Bookings.room_id, lookup_expr=eq)
    ordering = OrderingFilter(
        price=OrderingField(Bookings.price),
        date_from=OrderingField(Bookings.date_from, nulls=NullsPosition.last),
        date_to=OrderingField(Bookings.date_to, nulls=NullsPosition.last),
    )
