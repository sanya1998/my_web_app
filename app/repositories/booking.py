from app.common.dependencies.filters.bookings import BookingsFilterSchema, BookingsFilterSet
from app.common.exceptions.repositories.booking import BookingNotFoundErrorError
from app.common.schemas.booking import BookingSchema
from app.common.tables import Bookings
from app.repositories.base import BaseRepository


class BookingRepo(BaseRepository):
    db_model = Bookings
    schema_model = BookingSchema
    exception_not_found = BookingNotFoundErrorError
    filter_set = BookingsFilterSet
    filter_schema = BookingsFilterSchema
