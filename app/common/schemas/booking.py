from datetime import date, timedelta
from typing import List

from app.common.schemas.base import BaseSchema
from fastapi import Form
from pydantic import Field


class BookingBaseSchema(BaseSchema):
    date_from: date
    date_to: date


class BookingBaseInputSchema(BookingBaseSchema):
    date_from: date = Field(Form(date.today()))
    date_to: date = Field(Form(date.today() + timedelta(days=1)))


class BookingCreateInputSchema(BookingBaseInputSchema):
    """Бронирование создает пользователь, он не может указать цену. А room_id можно указать только при создании"""

    room_id: int = Field(Form(1))


class BookingUpdateInputSchema(BookingBaseInputSchema):
    """Бронирование редактирует менеджер, он не может изменить room_id, но может изменить цену"""

    id: int = Field(Form(1))
    price: int = Field(Form(0))


class BookingUpdateSchema(BookingBaseSchema):
    price: int


class BookingCreateSchema(BookingUpdateSchema):
    room_id: int
    user_id: int


class BookingReadSchema(BookingCreateSchema):
    id: int
    total_days: int
    total_cost: int


class CheckData(BaseSchema):
    selected_room_id: int
    check_into: date
    check_out: date
    exclude_booking_ids: List[int] = list()
