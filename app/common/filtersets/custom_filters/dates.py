from datetime import date

from app.common.tables import Bookings, Rooms
from sqlalchemy import Select, and_, func, label, or_, select
from sqlalchemy_filterset import BaseFilter


class DatesFilter(BaseFilter):
    """
    WITH booked_rooms AS (
        SELECT bookings.room_id AS room_id, count(bookings.room_id) AS occupied
        FROM bookings
        WHERE
            bookings.date_from >= '2024-05-05' AND bookings.date_from < '2024-05-06' OR
            bookings.date_from < '2024-05-05' AND bookings.date_to > '2024-05-05'
        GROUP BY bookings.room_id
    )
    SELECT *
    FROM rooms LEFT OUTER JOIN booked_rooms ON booked_rooms.room_id = rooms.id
    WHERE rooms.quantity > COALESCE(booked_rooms.occupied, 0)
    """

    def filter(self, query: Select, value: tuple[date, date] | None, values: dict) -> Select:
        if value is None:
            return query

        check_into, check_out = value
        days = (check_out - check_into).days
        # TODO: const "occupied", "remain_by_room"...
        booked_rooms = (
            select(Bookings.room_id, label("occupied", func.count(Bookings.room_id)))
            .where(
                or_(
                    and_(
                        Bookings.date_from >= check_into,
                        Bookings.date_from < check_out,
                    ),
                    and_(
                        Bookings.date_from < check_into,
                        Bookings.date_to > check_into,
                    ),
                ),
            )
            .group_by(Bookings.room_id)
        ).cte("booked_rooms")

        remain_by_room = label("remain_by_room", Rooms.quantity - func.coalesce(booked_rooms.c.occupied, 0))
        # TODO: разобраться, почему pycharm подчеркивает days * Rooms.price
        total_cost = label("total_cost", days * Rooms.price)

        query = (
            query.add_columns(remain_by_room, total_cost)
            .outerjoin(target=booked_rooms, onclause=booked_rooms.c.room_id == Rooms.id)
            .where(remain_by_room > 0)
        )

        return query
