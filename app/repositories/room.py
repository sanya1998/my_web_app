from app.common.dependencies.filters.rooms import RoomsFilters
from app.common.schemas.room import ManyRoomsReadSchema, RoomBaseReadSchema, RoomReadSchema
from app.common.tables import Bookings, Hotels, Rooms
from app.repositories.base import BaseRepository
from app.repositories.booking import BookingRepo
from sqlalchemy import Select, and_, func, label


class RoomRepo(BaseRepository):
    db_model = Rooms

    one_read_schema = RoomReadSchema
    many_read_schema = ManyRoomsReadSchema
    create_schema = RoomBaseReadSchema

    @BaseRepository.catcher
    def _modify_query_for_getting_objects(
        self, query: Select, filters: RoomsFilters, **additional_filters
    ) -> Select:  # TODO: types
        query = self.free_rooms_by_check_dates(query, filters.check_into, filters.check_out).join(
            Hotels, and_(Rooms.hotel_id == Hotels.id)
        )
        return query

    @BaseRepository.catcher
    def _modify_query_for_getting_object(self, query: Select, **filters):
        query = query.outerjoin(Hotels, Hotels.id == Rooms.hotel_id).add_columns(Hotels)
        return query

    @classmethod
    @BaseRepository.catcher
    def free_rooms_by_check_dates(cls, query: Select, check_into, check_out) -> Select:
        """
        Сколько будет свободных комнат (для всех типов комнат) в выбранные (проверяемые) даты заезда и выезда.
            SELECT rooms.id, rooms.quantity - count(rooms.id) AS remain
            FROM rooms LEFT OUTER JOIN bookings ON
                bookings.room_id = rooms.id
                AND (
                    check_into <= bookings.date_from AND bookings.date_from < check_out
                    OR
                    bookings.date_from < check_into AND check_into < bookings.date_to
                )
            GROUP BY rooms.id, rooms.quantity
            HAVING rooms.quantity - count(rooms.id) > 0
        :param query: запрос для редактирования
        :param check_into: планируемая дата заезда
        :param check_out: планируемая дата выезда
        :return: сформированный запрос
        """

        days = (check_out - check_into).days if check_out and check_into else 0
        total_cost = label("total_cost", days * Rooms.price)

        # TODO: "remain_by_room" потом используется в качестве поля. То есть при изменении могут быть проблемы
        remain_by_room = label("remain_by_room", Rooms.quantity - func.count(Bookings.id))

        query = (
            query.add_columns(remain_by_room, total_cost)
            .outerjoin(
                Bookings,
                onclause=and_(
                    Bookings.room_id == Rooms.id,
                    BookingRepo.clause_for_checking_dates(check_into, check_out),
                ),
            )
            .group_by(Rooms)
            .having(remain_by_room > 0)  # TODO: remain_by_room>0 в фильтры?, + отели без комнат тоже выводить
        )
        return query
