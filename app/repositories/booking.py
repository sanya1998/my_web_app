from app.common.filtersets.bookings import BookingsFiltersSet
from app.common.schemas.booking import (
    BookingCreateSchema,
    BookingInputSchema,
    BookingReadSchema,
)
from app.common.tables import Bookings, Rooms
from app.repositories.base import BaseRepository
from sqlalchemy import and_, func, label, or_, select


class BookingRepo(BaseRepository):
    db_model = Bookings

    read_schema = BookingReadSchema
    create_schema = BookingCreateSchema

    filter_set = BookingsFiltersSet

    @BaseRepository.catcher
    async def get_room_info(self, booking_input: BookingInputSchema):
        """
        -- Показать, сколько осталось свободных номеров данного типа комнат на указанный период
        WITH
            ids (selected_room_id) AS (VALUES (1)),
            dates (check_into, check_out) AS (VALUES ('2024-07-10'::date, '2024-07-20'::date)),
            booked_rooms AS (
                SELECT bookings.room_id
                FROM ids, dates, bookings
                WHERE
                    bookings.room_id = selected_room_id AND
                    (
                        date_from >= check_into AND date_from < check_out OR
                        date_from < check_into AND date_to > check_into
                    )
            )
        -- Получить id, цену и остаток данного типа комнат
        SELECT rooms.id AS room_id, rooms.price, rooms.quantity - COUNT(booked_rooms.room_id) AS remain
        FROM
            ids,
            rooms LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        WHERE rooms.id = selected_room_id
        GROUP BY rooms.id, rooms.price;
        """
        selected_room_id = booking_input.room_id
        check_into, check_out = booking_input.date_from, booking_input.date_to

        booked_rooms = (
            select(self.db_model.room_id).where(
                and_(
                    self.db_model.room_id == selected_room_id,
                    or_(
                        and_(
                            self.db_model.date_from >= check_into,
                            self.db_model.date_from < check_out,
                        ),
                        and_(
                            self.db_model.date_from < check_into,
                            self.db_model.date_to > check_into,
                        ),
                    ),
                )
            )
        ).cte()

        selected_room_query = (
            select(Rooms.id, Rooms.price, label("remain", Rooms.quantity - func.count(booked_rooms.c.room_id)))
            .select_from(Rooms)
            .outerjoin(target=booked_rooms, onclause=booked_rooms.c.room_id == Rooms.id)
            .where(and_(Rooms.id == selected_room_id))  # TODO: без `and_` можно?
            .group_by(Rooms.id, Rooms.price)
        )

        selected_room_answer = await self.session.execute(selected_room_query)
        return selected_room_answer.one_or_none()
