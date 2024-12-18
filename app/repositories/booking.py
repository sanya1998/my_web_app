from app.common.filtersets.bookings import BookingsFiltersSet
from app.common.helpers.db import get_columns_by_table
from app.common.schemas.booking import (
    BookingCreateSchema,
    CheckData,
    ManyBookingsReadSchema,
    OneBookingReadSchema,
    OneBookingWithJoinReadSchema,
    OneCreatedBookingReadSchema,
    OneDeletedBookingReadSchema,
    OneUpdatedBookingReadSchema,
)
from app.common.tables import Bookings, Rooms
from app.repositories.base import BaseRepository
from sqlalchemy import Select, and_, func, label, or_, select


class BookingRepo(BaseRepository):
    db_model = Bookings

    one_read_schema = OneBookingReadSchema
    one_read_join_schema = OneBookingWithJoinReadSchema
    many_read_schema = ManyBookingsReadSchema
    one_created_read_schema = OneCreatedBookingReadSchema
    one_updated_read_schema = OneUpdatedBookingReadSchema
    one_deleted_read_schema = OneDeletedBookingReadSchema
    create_schema = BookingCreateSchema

    filter_set = BookingsFiltersSet

    @BaseRepository.catcher
    def _create_query_for_getting_object_with_join(self, **filters) -> Select:
        return select(self.db_model, Rooms).filter_by(**filters).join(Rooms)

    @BaseRepository.catcher
    def _create_query_for_getting_objects(self) -> Select:
        return select(get_columns_by_table(self.db_model), get_columns_by_table(Rooms)).join(Rooms)

    @BaseRepository.catcher
    async def get_room_info_by_id_and_dates(self, data: CheckData):
        """
        -- Показать, сколько осталось свободных номеров данного типа комнат на указанный период
        WITH
            ids (selected_room_id, exclude_booking_ids) AS (VALUES (1, array [1])),
            dates (check_into, check_out) AS (VALUES ('2024-07-10'::date, '2024-07-20'::date)),
            booked_rooms AS (
                SELECT bookings.room_id
                FROM ids, dates, bookings
                WHERE
                    bookings.room_id = selected_room_id AND
                    (
                        array_length(exclude_booking_ids, 1) = 0 OR
                        NOT bookings.id = ANY (exclude_booking_ids)
                    ) AND
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
        booked_rooms = (
            select(self.db_model.room_id).where(
                and_(
                    self.db_model.room_id == data.selected_room_id,
                    or_(len(data.exclude_booking_ids) == 0, self.db_model.id.notin_(data.exclude_booking_ids)),
                    or_(
                        and_(
                            self.db_model.date_from >= data.check_into,
                            self.db_model.date_from < data.check_out,
                        ),
                        and_(
                            self.db_model.date_from < data.check_into,
                            self.db_model.date_to > data.check_into,
                        ),
                    ),
                )
            )
        ).cte()

        # TODO: привести к единообразию remain, remain_by_room, remain_by_hotel
        selected_room_query = (
            select(Rooms.id, Rooms.price, label("remain", Rooms.quantity - func.count(booked_rooms.c.room_id)))
            .select_from(Rooms)
            .outerjoin(target=booked_rooms, onclause=booked_rooms.c.room_id == Rooms.id)
            .where(and_(Rooms.id == data.selected_room_id))  # TODO: без `and_` можно?
            .group_by(Rooms.id, Rooms.price)
        )
        selected_room_answer = await self.session.execute(selected_room_query)
        return selected_room_answer.one_or_none()
