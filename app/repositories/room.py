from app.common.constants.db_fields import REMAIN_BY_ROOM, TOTAL_COST
from app.common.dependencies.filters import RoomsFilters
from app.common.helpers.check_data import CheckData
from app.common.helpers.db import get_columns_by_table
from app.common.schemas.room import ManyRoomsReadSchema, RoomBaseReadSchema, RoomReadSchema
from app.common.tables import Bookings, Hotels, Rooms
from app.repositories.base import BaseRepository
from sqlalchemy import ColumnElement, Select, and_, func, label, or_, select


class RoomRepo(BaseRepository):
    db_model = Rooms

    one_read_schema = RoomReadSchema
    many_read_schema = ManyRoomsReadSchema

    create_schema = RoomBaseReadSchema

    @BaseRepository.catcher
    def _modify_query_for_getting_objects(self, query: Select, filters: RoomsFilters, **additional_filters) -> Select:
        return (
            self.free_rooms_query_by_booking_dates(
                data=CheckData(check_into=filters.check_into, check_out=filters.check_out)
            )
            .outerjoin(Hotels, and_(Hotels.id == Rooms.hotel_id))
            .add_columns(Hotels)
            .group_by(Hotels)
            .select_from(Rooms)
        )

    @BaseRepository.catcher
    def _modify_query_for_getting_object(self, query: Select, **filters):
        query = query.outerjoin(Hotels, and_(Hotels.id == Rooms.hotel_id)).add_columns(Hotels)
        return query

    @staticmethod
    @BaseRepository.catcher
    def checking_dates_clause(check_into, check_out) -> ColumnElement[bool]:
        """
        Если выполняется это условие, то планируемые даты задевают существующее бронирование
            check_into <= bookings.date_from AND bookings.date_from < check_out
            OR
            bookings.date_from < check_into AND check_into < bookings.date_to
        :param check_into: планируемая дата заезда
        :param check_out: планируемая дата выезда
        :return:
        """
        if check_into and check_out:
            clause = or_(
                and_(check_into <= Bookings.date_from, Bookings.date_from < check_out),
                and_(Bookings.date_from < check_into, check_into < Bookings.date_to),
            )
        else:
            clause = False
        return clause

    @classmethod
    @BaseRepository.catcher
    def free_rooms_query_by_booking_dates(cls, data: CheckData):
        """
            -- Получить типы комнат со свободными комнатами в выбранные (проверяемые) даты заезда и выезда.
        WITH
            ids (selected_room_id, exclude_booking_ids) AS (VALUES (1, array [1])),
            dates (check_into, check_out) AS (VALUES ('2024-07-10'::date, '2024-07-20'::date)),
            bookings_by_dates AS (
                SELECT bookings.room_id AS room_id
                FROM bookings
                WHERE clause_for_checking_dates
            )
                SELECT
                    rooms.*,
                    rooms.quantity - count(bookings_by_dates.room_id) AS remain_by_room,
                    (check_out - check_into).days * rooms.price AS total_cost
                FROM rooms LEFT OUTER JOIN bookings_by_dates ON bookings_by_dates.room_id = rooms.id
                GROUP BY rooms.*
                HAVING rooms.quantity - count(bookings_by_dates.room_id) > 0
        """

        bookings_by_dates = (
            select(Bookings.room_id).where(
                and_(
                    cls.checking_dates_clause(data.check_into, data.check_out),
                    or_(len(data.exclude_booking_ids) == 0, Bookings.id.notin_(data.exclude_booking_ids)),
                )
            )
        ).cte("bookings_by_dates")

        days = (data.check_out - data.check_into).days if data.check_out and data.check_into else 0
        total_cost = label(TOTAL_COST, days * Rooms.price)

        remain_by_room = label(REMAIN_BY_ROOM, Rooms.quantity - func.count(bookings_by_dates.c.room_id))

        query = (
            select(get_columns_by_table(Rooms), remain_by_room, total_cost)
            .outerjoin(target=bookings_by_dates, onclause=and_(bookings_by_dates.c.room_id == Rooms.id))
            .group_by(Rooms)
            .having(remain_by_room > 0)
        )
        return query

    @BaseRepository.catcher
    async def get_room_by_id_and_dates(self, check_data: CheckData, room_id: int):
        """
        SELECT *
        FROM get_free_rooms_by_booking_dates
        WHERE rooms.id = 7
        """
        selected_room_query = self.free_rooms_query_by_booking_dates(check_data).where(Rooms.id == room_id)
        selected_room_answer = await self.session.execute(selected_room_query)
        return selected_room_answer.one_or_none()
