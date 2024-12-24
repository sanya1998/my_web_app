from typing import List

from app.common.dependencies.parameters.base import Parameters
from app.common.filtersets.hotels import HotelsFiltersSet
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
from sqlalchemy import Column, Result, Select, func, label, select
from sqlalchemy.orm import selectinload


class HotelRepo(BaseRepository):
    db_model = Hotels

    one_read_schema = OneHotelReadSchema
    one_read_join_schema = OneHotelWithJoinReadSchema
    many_read_schema = ManyHotelsReadSchema
    one_created_read_schema = OneCreatedHotelReadSchema
    one_updated_read_schema = OneUpdatedHotelReadSchema
    one_deleted_read_schema = OneDeletedHotelReadSchema
    create_schema = HotelCreateSchema

    filter_set = HotelsFiltersSet

    @BaseRepository.catcher
    def _create_query_for_getting_objects(self) -> Select:
        return select(self.db_model).options(selectinload(self.db_model.rooms)).group_by(self.db_model)

    @BaseRepository.catcher
    def _modify_query_for_getting_objects(self, query: Select, parameters: Parameters) -> Select:
        # TODO: это работает, но мне не нравится, что есть константы, и что pycharm подчеркивает t.name
        joined_tables = {t.name for t in query.columns_clause_froms if hasattr(t, "name")}

        # Если есть join с Bookings
        if "booked_rooms" in joined_tables:
            remain_by_hotel = label("remain_by_hotel", func.sum(Rooms.quantity - func.coalesce(Column("occupied"), 0)))
            query = query.with_only_columns(
                get_columns_by_table(self.db_model)
            ).add_columns(  # Чтобы не брать remain_by_room
                remain_by_hotel
            )
        return query

    def _validate_result_for_getting_objects(self, result: Result) -> List[many_read_schema]:
        filtered_objects = result.scalars().all()
        return [self.many_read_schema.model_validate(obj) for obj in filtered_objects]

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
