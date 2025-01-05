from datetime import date

from app.common.schemas.base import BaseSchema
from app.common.schemas.room import RoomReadSchema
from app.common.schemas.user import UserBaseReadSchema
from pydantic import AliasChoices, Field


class BookingBaseSchema(BaseSchema):
    date_from: date
    date_to: date


class BookingUpdateSchema(BookingBaseSchema):
    price: int


class BookingCreateSchema(BookingUpdateSchema):
    room_id: int
    user_id: int


class BookingBaseReadSchema(BookingCreateSchema):
    id: int
    total_days: int
    total_cost: int


class CurrentUserBookingReadSchema(BookingBaseReadSchema):
    room_id: int | None = Field(None, exclude=True)
    room: RoomReadSchema = Field(validation_alias=AliasChoices("room", "Rooms"))


class BookingReadSchema(CurrentUserBookingReadSchema):
    user_id: int | None = Field(None, exclude=True)
    user: UserBaseReadSchema = Field(validation_alias=AliasChoices("user", "Users"))
