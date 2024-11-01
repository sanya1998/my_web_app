from datetime import date
from typing import List

from app.common.constants.datetimes import TODAY, TOMORROW
from app.common.schemas.base import BaseSchema
from app.common.schemas.room import RoomBaseSchema
from fastapi import Form
from pydantic import Field


class BookingBaseSchema(BaseSchema):
    date_from: date
    date_to: date


class BookingBaseInputSchema(BookingBaseSchema):
    date_from: date = Field(Form(TODAY))
    date_to: date = Field(Form(TOMORROW))


class BookingCreateInputSchema(BookingBaseInputSchema):
    """Бронирование создает пользователь, он не может указать цену. А room_id можно указать только при создании"""

    room_id: int = Field(Form(1))


class BookingUpdateInputSchema(BookingBaseInputSchema):
    """Бронирование редактирует менеджер, он не может изменить room_id, но может изменить цену"""

    price: int = Field(Form(0))


class BookingUpdateSchema(BookingBaseSchema):
    price: int


class BookingCreateSchema(BookingUpdateSchema):
    room_id: int
    user_id: int


class BaseBookingReadSchema(BookingCreateSchema):
    id: int
    total_days: int
    total_cost: int


class OneBookingReadSchema(BaseBookingReadSchema):
    pass


class OneCreatedBookingReadSchema(BaseBookingReadSchema):
    pass


class OneUpdatedBookingReadSchema(BaseBookingReadSchema):
    pass


class OneBookingWithJoinReadSchema(BaseBookingReadSchema):
    room: RoomBaseSchema


class ManyBookingsReadSchema(BaseBookingReadSchema):
    # TODO: prefix room_
    # TODO: не дублировать поля из Rooms
    name: str
    description: str | None = None
    services: List[str] = Field(default=list())
    image_id: int | None = None


class OneDeletedBookingReadSchema(BaseBookingReadSchema):
    pass


class CheckData(BaseSchema):
    selected_room_id: int
    check_into: date
    check_out: date
    exclude_booking_ids: List[int] = list()
