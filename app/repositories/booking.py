from app.common.dependencies.api_args.bookings import BookingsFilterSchema
from app.common.exceptions.repositories.booking import BookingNotFoundError, BookingTypeError
from app.common.filtersets.bookings import BookingsFilterSet
from app.common.schemas.booking import BookingSchema
from app.common.tables import Bookings
from app.repositories.base import BaseRepository


class BookingRepo(BaseRepository):
    db_model = Bookings
    schema_model = BookingSchema
    exception_not_found = BookingNotFoundError
    exception_type = BookingTypeError
    filter_set = BookingsFilterSet
    filter_schema = BookingsFilterSchema
