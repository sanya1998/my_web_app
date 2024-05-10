from datetime import date

from app.common.models.base import Base


class SBooking(Base):
    room_id: int
    date_from: date
    date_to: date
