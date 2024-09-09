from datetime import date

from app.common.filtersets.custom_filters.join_hotels_rooms import join_hotels_rooms
from app.common.tables import Bookings, Rooms, Hotels
from sqlalchemy import Select, and_, func, or_, select
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
    LIMIT 10 OFFSET 0;
    """

    def filter(self, query: Select, value: tuple[date, date] | None, values: dict) -> Select:
        if value is None:
            return query

        query = join_hotels_rooms(query, values)

        check_into, check_out = value
        booked_rooms = (
            select(Bookings.room_id, func.count(Bookings.room_id).label("occupied"))
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
        ).cte()

        query = query.outerjoin(target=booked_rooms, onclause=booked_rooms.c.room_id == Rooms.id).where(
            Rooms.quantity > func.coalesce(booked_rooms.c.occupied, 0)
        )

        return query
