from app.common.dependencies.parameters.base import Parameters
from app.common.filtersets.rooms import RoomsFiltersSet
from app.common.schemas.room import (
    ManyRoomsReadSchema,
    OneRoomReadSchema,
    RoomCreateSchema,
)
from app.common.tables import Bookings, Rooms
from app.repositories.base import BaseRepository
from app.repositories.booking import BookingRepo
from sqlalchemy import Select, and_, func, label


class RoomRepo(BaseRepository):
    db_model = Rooms

    one_read_schema = OneRoomReadSchema
    many_read_schema = ManyRoomsReadSchema
    create_schema = RoomCreateSchema

    filter_set = RoomsFiltersSet

    @BaseRepository.catcher
    def _modify_query_for_getting_objects(self, query: Select, parameters: Parameters) -> Select:
        return self.free_rooms_by_check_dates(query, parameters.filters.check_into, parameters.filters.check_out)

    @BaseRepository.catcher
    def free_rooms_by_check_dates(self, query: Select, check_into, check_out) -> Select:
        """
        Сколько будет свободных комнат (для всех типов комнат) в выбранные (проверяемые) даты заезда и выезда.
            SELECT rooms.id, rooms.quantity - count(rooms.id) AS remain
            FROM rooms LEFT OUTER JOIN bookings ON
                bookings.room_id = rooms.id
                AND (
                    bookings.date_from >= check_into AND bookings.date_from < check_out
                    OR
                    bookings.date_from < check_into AND bookings.date_to > check_into
                )
            GROUP BY rooms.id, rooms.quantity
            HAVING rooms.quantity - count(rooms.id) > 0
        :param query: запрос для редактирования
        :param check_into: планируемая дата заезда
        :param check_out: планируемая дата выезда
        :return: сформированный запрос
        """
        # TODO: "remain_by_room" вынести в константы
        remain_field = label("remain_by_room", Rooms.quantity - func.count(Bookings.id))
        query = (
            query.add_columns(remain_field)
            .outerjoin(
                Bookings,
                onclause=and_(
                    Bookings.room_id == Rooms.id,
                    BookingRepo.clause_for_checking_dates(check_into, check_out),
                ),
            )
            .group_by(Rooms.id, Rooms.quantity)
            .having(remain_field > 0)
        )
        return query
