from app.common.dependencies.filters.bookings import BookingsFilters
from app.common.schemas.booking import BookingBaseReadSchema, BookingCreateSchema, BookingReadSchema
from app.common.tables import Bookings, Hotels, Rooms, Users
from app.repositories.base import BaseRepository
from sqlalchemy import Select


class BookingRepo(BaseRepository):
    db_model = Bookings

    one_read_schema = BookingReadSchema
    many_read_schema = BookingReadSchema
    one_created_read_schema = BookingBaseReadSchema
    one_updated_read_schema = BookingBaseReadSchema
    one_deleted_read_schema = BookingBaseReadSchema

    create_schema = BookingCreateSchema

    def _add_user_room_hotel(self, query: Select) -> Select:
        return (
            query.outerjoin(Users, Bookings.user_id == Users.id)  # TODO: pycharm подчеркивает при добавлении ': Select'
            .outerjoin(Rooms, Bookings.room_id == Rooms.id)
            .outerjoin(Hotels, Rooms.hotel_id == Hotels.id)
            .add_columns(Users, Rooms, Hotels)
        )

    def _modify_query_for_getting_objects(
        self, query: Select, filters: BookingsFilters, **additional_filters
    ) -> Select:
        return self._add_user_room_hotel(query)

    @BaseRepository.catcher
    def _modify_query_for_getting_object(self, query: Select, **filters):
        return self._add_user_room_hotel(query)
