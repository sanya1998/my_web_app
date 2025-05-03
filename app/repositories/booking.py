from typing import List

from app.common.dependencies.filters.base import BaseFilters
from app.common.dependencies.filters.bookings import BookingsFilters
from app.common.exceptions.repositories.multiple_results import MultipleResultsRepoError
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.helpers.db import get_columns_by_table
from app.common.schemas.booking import (
    BookingBaseReadSchema,
    BookingCreateSchema,
    BookingReadSchema,
    CurrentUserBookingReadSchema,
)
from app.common.tables import Bookings, Hotels, Rooms, Users
from app.repositories.base import BaseRepository
from sqlalchemy import Select, select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound


class BookingRepo(BaseRepository):
    db_model = Bookings

    one_read_schema = BookingReadSchema
    many_read_schema = BookingReadSchema
    one_created_read_schema = BookingBaseReadSchema
    one_updated_read_schema = BookingBaseReadSchema
    one_deleted_read_schema = BookingBaseReadSchema

    create_schema = BookingCreateSchema

    @BaseRepository.catcher
    def _add_user(self, query: Select) -> Select:
        return query.outerjoin(
            Users, Bookings.user_id == Users.id  # TODO: pycharm подчеркивает при добавлении ': Select'
        ).add_columns(Users)

    @BaseRepository.catcher
    def _add_room_hotel(self, query: Select) -> Select:
        return (
            query.outerjoin(Rooms, Bookings.room_id == Rooms.id)  # TODO: pycharm подчеркивает при добавлении ': Select'
            .outerjoin(Hotels, Rooms.hotel_id == Hotels.id)
            .add_columns(Rooms, Hotels)
        )

    @BaseRepository.catcher
    def _add_user_room_hotel(self, query: Select) -> Select:
        query = self._add_user(query)
        query = self._add_room_hotel(query)
        return query

    @BaseRepository.catcher
    def _modify_query_for_getting_objects(
        self, query: Select, filters: BookingsFilters, **additional_filters
    ) -> Select:
        return self._add_user_room_hotel(query)

    @BaseRepository.catcher
    def _modify_query_for_getting_object(self, query: Select, **filters):
        return self._add_user_room_hotel(query)

    @BaseRepository.catcher
    async def get_objects_self(
        self, filters: BookingsFilters, **additional_filters
    ) -> List[CurrentUserBookingReadSchema]:
        query = select(get_columns_by_table(self.db_model))
        query = self._add_room_hotel(query)
        query = filters.modify_query(query, **additional_filters)
        result = await self.execute(query)
        filtered_objects = result.all()
        return [CurrentUserBookingReadSchema.model_validate(obj) for obj in filtered_objects]

    @BaseRepository.catcher
    async def get_object_self(self, **filters) -> CurrentUserBookingReadSchema:
        query = select(get_columns_by_table(self.db_model))
        query = BaseFilters().set_db_model(self.db_model).modify_query(query, **filters)
        query = self._add_room_hotel(query)
        result = await self.execute(query)
        try:
            obj = result.one()
        except NoResultFound:
            raise NotFoundRepoError
        except MultipleResultsFound:
            raise MultipleResultsRepoError
        return CurrentUserBookingReadSchema.model_validate(obj)
