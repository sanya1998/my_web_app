from datetime import date
from typing import List

from app.common.constants.datetimes import TODAY, TOMORROW
from app.common.schemas.base import BaseSchema
from app.common.schemas.room import RoomBaseReadSchema
from app.common.schemas.user import UserBaseReadSchema
from fastapi import Form
from pydantic import AliasChoices, Field


class BookingBaseInputSchema(BaseSchema):
    date_from: date = Field(Form(description=f"Example: {TODAY}"))
    date_to: date = Field(Form(description=f"Example: {TOMORROW}"))


class BookingCreateInputSchema(BookingBaseInputSchema):
    """Бронирование создает пользователь, он не может указать цену. А room_id можно указать только при создании"""

    room_id: int = Field(Form())


class BookingUpdateInputSchema(BookingBaseInputSchema):
    """Бронирование редактирует менеджер, он не может изменить room_id, но может изменить цену"""

    price: int = Field(Form(ge=0))


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
    # TODO: room: RoomReadSchema (С hotel)
    room: RoomBaseReadSchema = Field(validation_alias=AliasChoices("room", "Rooms"))


class BookingReadSchema(CurrentUserBookingReadSchema):
    user_id: int | None = Field(None, exclude=True)
    user: UserBaseReadSchema = Field(validation_alias=AliasChoices("user", "Users"))


# TODO: точно здесь ?
class CheckData(BaseSchema):
    selected_room_id: int
    check_into: date
    check_out: date
    exclude_booking_ids: List[int] = list()
