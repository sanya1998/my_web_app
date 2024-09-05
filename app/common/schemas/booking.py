from datetime import date

from app.common.schemas.base import BaseSchema


class BookingSchemaBase(BaseSchema):
    pass


class BookingInputSchema(BookingSchemaBase):
    room_id: int
    date_from: date
    date_to: date


class BookingCreateSchema(BookingInputSchema):
    price: int
    user_id: int


class BookingReadSchema(BookingCreateSchema):
    id: int
    total_days: int
    total_cost: int
