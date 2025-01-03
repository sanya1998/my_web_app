from app.common.dependencies.filters.hotels import HotelsFilters
from app.common.dependencies.input.hotels import HotelBaseInput
from app.common.helpers.db import get_columns_by_table
from app.common.schemas.hotel import HotelBaseReadSchema, HotelReadSchema, ManyHotelsReadSchema
from app.common.tables import Hotels, Rooms
from app.repositories.base import BaseRepository
from app.repositories.room import RoomRepo
from sqlalchemy import Select, and_, func, label, select


class HotelRepo(BaseRepository):
    db_model = Hotels

    one_read_schema = HotelReadSchema
    many_read_schema = ManyHotelsReadSchema
    one_created_read_schema = HotelBaseReadSchema
    one_updated_read_schema = HotelBaseReadSchema
    one_deleted_read_schema = HotelBaseReadSchema
    create_schema = HotelBaseInput

    @BaseRepository.catcher
    def _modify_query_for_getting_objects(
        self, query: Select, filters: HotelsFilters, **additional_filters
    ) -> Select:  # TODO types
        rooms = select(get_columns_by_table(Rooms))
        free_rooms = RoomRepo.free_rooms_by_check_dates(rooms, filters.rooms.check_into, filters.rooms.check_out).cte(
            "free_rooms"
        )
        free_rooms_c = free_rooms.c
        filters.rooms.set_db_model(free_rooms_c)
        # TODO: "remain_by_hotel" вынести в константы. Либо по-другому решить то, что потом оно используется как поле
        remain_field = label("remain_by_hotel", func.sum(free_rooms_c.remain_by_room))
        query = (
            query.join(
                free_rooms, onclause=and_(Hotels.id == free_rooms_c.hotel_id, *filters.rooms.get_where_clauses())
            )
            .add_columns(remain_field)
            .group_by(Hotels)
        )
        return query

    @BaseRepository.catcher
    def _modify_query_for_getting_object(self, query: Select, **filters):
        return (
            query.add_columns(label("rooms_quantity", func.count(Rooms.id)))  # TODO: имеется в виду, количество типов
            .outerjoin(Rooms, Hotels.id == Rooms.hotel_id)
            .group_by(Hotels)
        )
