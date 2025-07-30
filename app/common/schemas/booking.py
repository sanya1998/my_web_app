from datetime import date
from typing import Annotated

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
    user_id: Annotated[int | None, Field(exclude=True)] = None
    room_id: Annotated[int | None, Field(exclude=True)] = None
    room: Annotated[RoomReadSchema, Field(validation_alias=AliasChoices("room", "Rooms"))]


class BookingReadSchema(CurrentUserBookingReadSchema):
    user: Annotated[UserBaseReadSchema, Field(validation_alias=AliasChoices("user", "Users"))]
