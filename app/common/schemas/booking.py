from datetime import date

from app.common.schemas.base import BaseSchema


class BookingSchema(BaseSchema):
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_days: int
    total_cost: int
