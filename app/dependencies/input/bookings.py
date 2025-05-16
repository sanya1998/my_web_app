from datetime import date
from typing import Annotated

from app.common.constants.datetimes import TODAY, TOMORROW
from app.dependencies.input.base import BaseInput
from fastapi import Form
from pydantic import Field


class BookingBaseInput(BaseInput):
    date_from: Annotated[date, Field(description=f"Example: {TODAY}")]
    date_to: Annotated[date, Field(description=f"Example: {TOMORROW}")]


class BookingCreateInputSchema(BookingBaseInput):
    """Бронирование создает пользователь, он не может указать цену. А room_id можно указать только при создании"""

    room_id: int


class BookingUpdateInputSchema(BookingBaseInput):
    """Бронирование редактирует менеджер, он не может изменить room_id, но может изменить цену"""

    price: Annotated[int, Field(ge=0)]


BookingInputCreateDep = Annotated[BookingCreateInputSchema, Form()]
BookingInputUpdateDep = Annotated[BookingUpdateInputSchema, Form()]
