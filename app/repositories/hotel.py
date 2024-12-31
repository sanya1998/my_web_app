from app.common.dependencies.filters.hotels import HotelsFilters
from app.common.helpers.db import get_columns_by_table
from app.common.schemas.hotel import (
    HotelCreateSchema,
    ManyHotelsReadSchema,
    OneCreatedHotelReadSchema,
    OneDeletedHotelReadSchema,
    OneHotelReadSchema,
    OneHotelWithJoinReadSchema,
    OneUpdatedHotelReadSchema,
)
from app.common.tables import Hotels, Rooms
from app.repositories.base import BaseRepository
from app.repositories.room import RoomRepo
from sqlalchemy import Select, and_, func, label, select


class HotelRepo(BaseRepository):
    db_model = Hotels

    one_read_schema = OneHotelReadSchema
    one_read_join_schema = OneHotelWithJoinReadSchema
    many_read_schema = ManyHotelsReadSchema
    one_created_read_schema = OneCreatedHotelReadSchema
    one_updated_read_schema = OneUpdatedHotelReadSchema
    one_deleted_read_schema = OneDeletedHotelReadSchema
    create_schema = HotelCreateSchema

    @BaseRepository.catcher
    def _modify_query_for_getting_objects(
        self, query: Select, filters: HotelsFilters, **additional_filters
    ) -> Select:  # TODO types
        rooms = select(get_columns_by_table(Rooms))
        free_rooms = RoomRepo.free_rooms_by_check_dates(rooms, filters.rooms.check_into, filters.rooms.check_out).cte(
            "free_rooms"
        )
        free_rooms_c = free_rooms.c
        filters.rooms._db_model = free_rooms_c
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
    def _create_query_for_getting_object_with_join(self, **filters) -> Select:
        return (
            select(self.db_model, label("rooms_quantity", func.count(Rooms.id)))
            .filter_by(**filters)
            .outerjoin(Rooms)
            .group_by(self.db_model)
        )

    @BaseRepository.catcher
    def _model_validate_for_getting_object_with_join(self, *objects) -> one_read_join_schema:
        return self.one_read_join_schema(rooms_quantity=objects[1], **objects[0].__dict__)
