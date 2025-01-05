from app.common.constants.db_fields import REMAIN_BY_HOTEL, ROOMS_QUANTITY
from app.common.dependencies.filters.hotels import HotelsFilters
from app.common.dependencies.input.hotels import HotelBaseInput
from app.common.helpers.check_data import CheckData
from app.common.schemas.hotel import HotelBaseReadSchema, HotelReadSchema, ManyHotelsReadSchema
from app.common.tables import Hotels, Rooms
from app.repositories.base import BaseRepository
from app.repositories.room import RoomRepo
from sqlalchemy import Select, and_, func, label


class HotelRepo(BaseRepository):
    db_model = Hotels

    one_read_schema = HotelReadSchema
    many_read_schema = ManyHotelsReadSchema
    one_created_read_schema = HotelBaseReadSchema
    one_updated_read_schema = HotelBaseReadSchema
    one_deleted_read_schema = HotelBaseReadSchema
    create_schema = HotelBaseInput

    @BaseRepository.catcher
    def _modify_query_for_getting_objects(self, query: Select, filters: HotelsFilters, **additional_filters) -> Select:
        free_rooms = RoomRepo.free_rooms_query_by_booking_dates(
            data=CheckData(check_into=filters.rooms.check_into, check_out=filters.rooms.check_out)
        ).cte("free_rooms")
        free_rooms_c = free_rooms.c
        filters.rooms.set_db_model(free_rooms_c)

        remain_by_hotel = label(REMAIN_BY_HOTEL, func.sum(free_rooms_c.remain_by_room))
        query = (
            query.outerjoin(
                free_rooms, onclause=and_(Hotels.id == free_rooms_c.hotel_id, *filters.rooms.get_where_clauses())
            )
            .add_columns(remain_by_hotel)
            .group_by(Hotels)
        )
        return query

    @BaseRepository.catcher
    def _modify_query_for_getting_object(self, query: Select, **filters):
        return (
            query.add_columns(label(ROOMS_QUANTITY, func.count(Rooms.id)))
            .outerjoin(Rooms, Hotels.id == Rooms.hotel_id)
            .group_by(Hotels)
        )
