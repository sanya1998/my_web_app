from app.common.dependencies.filters.bookings import BookingsFilters
from app.common.helpers.check_data import CheckData
from app.common.schemas.booking import BookingBaseReadSchema, BookingCreateSchema, BookingReadSchema
from app.common.tables import Bookings, Hotels, Rooms, Users
from app.repositories.base import BaseRepository
from sqlalchemy import ColumnElement, Select, and_, func, label, or_, select


class BookingRepo(BaseRepository):
    db_model = Bookings

    one_read_schema = BookingReadSchema
    many_read_schema = BookingReadSchema
    one_created_read_schema = BookingBaseReadSchema
    one_updated_read_schema = BookingBaseReadSchema
    one_deleted_read_schema = BookingBaseReadSchema
    create_schema = BookingCreateSchema

    def _modify_query_for_getting_objects(
        self, query: Select, filters: BookingsFilters, **additional_filters
    ) -> Select:
        # TODO: .outerjoin(Hotels, Rooms.hotel_id == Hotels.id),
        return (
            query.join(Users, Bookings.user_id == Users.id)  # TODO: pycharm подчеркивает только это почему-то
            .join(Rooms, Bookings.room_id == Rooms.id)
            .join(Hotels, Rooms.hotel_id == Hotels.id)  # TODO: сравнить с get object
            .select_from(Bookings)  # TODO: check
            .add_columns(Users, Rooms)
        )

    @BaseRepository.catcher
    def _modify_query_for_getting_object(self, query: Select, **filters):
        # TODO: {"booking: "{"room": {"hotel": {...}}}}
        # TODO: .outerjoin(Hotels, Rooms.hotel_id == Hotels.id),
        return (
            query.outerjoin(Users, Bookings.user_id == Users.id)
            .outerjoin(Rooms, Bookings.room_id == Rooms.id)
            .add_columns(Users, Rooms)
        )

    @staticmethod
    @BaseRepository.catcher
    def clause_for_checking_dates(check_into, check_out) -> ColumnElement[bool]:
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
    def query_for_getting_bookings_by_check_dates(cls, check_into, check_out) -> Select:
        """
        Создать запрос для получения бронирований, задевающие выбранные (проверяемые) даты заезда и выезда.
        SELECT bookings.room_id
        FROM bookings
        WHERE check_into <= date_from AND date_from < check_out OR date_from < check_into AND check_into < date_to
        :param check_into: планируемая дата заезда
        :param check_out: планируемая дата выезда
        :return: сформированный запрос
        """
        rooms_bookings = select(Bookings.room_id).where(cls.clause_for_checking_dates(check_into, check_out))
        return rooms_bookings

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
                         check_into <= date_from AND date_from < check_out OR
                        date_from < check_into AND check_into < date_to
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
        # TODO: нет ли ничего общего с RoomRepo.free_rooms_by_check_dates ?

        room_bookings = (
            self.query_for_getting_bookings_by_check_dates(data.check_into, data.check_out).where(
                and_(
                    self.db_model.room_id == data.selected_room_id,
                    or_(len(data.exclude_booking_ids) == 0, self.db_model.id.notin_(data.exclude_booking_ids)),
                )
            )
        ).cte()

        remain_by_room = label("remain_by_room", Rooms.quantity - func.count(room_bookings.c.room_id))
        selected_room_query = (
            select(Rooms.id, Rooms.price, remain_by_room)
            .select_from(Rooms)
            .outerjoin(target=room_bookings, onclause=and_(room_bookings.c.room_id == Rooms.id))
            .where(Rooms.id == data.selected_room_id)  # TODO: 2 раза
            .group_by(Rooms)
        )
        selected_room_answer = await self.session.execute(selected_room_query)
        return selected_room_answer.one_or_none()
