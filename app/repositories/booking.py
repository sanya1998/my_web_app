from app.common.exceptions.repositories.booking import BookingNotFound
from app.common.models.booking import SBooking
from app.common.tables import Bookings
from app.repositories.base import BaseRepository


class BookingRepo(BaseRepository):
    db_model = Bookings
    schema_model = SBooking
    exception_not_found = BookingNotFound
