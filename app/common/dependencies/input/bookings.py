from datetime import date
from typing import Annotated

from app.common.constants.datetimes import TODAY, TOMORROW
from app.common.dependencies.input.base import BaseInput
from fastapi import Depends, Form
from pydantic import Field


class BookingBaseInput(BaseInput):
    date_from: date = Field(Form(description=f"Example: {TODAY}"))
    date_to: date = Field(Form(description=f"Example: {TOMORROW}"))


class BookingCreateInputSchema(BookingBaseInput):
    """Бронирование создает пользователь, он не может указать цену. А room_id можно указать только при создании"""

    room_id: int = Field(Form())


class BookingUpdateInputSchema(BookingBaseInput):
    """Бронирование редактирует менеджер, он не может изменить room_id, но может изменить цену"""

    price: int = Field(Form(ge=0))


BookingInputCreateDep = Annotated[BookingCreateInputSchema, Depends(BookingCreateInputSchema)]
BookingInputUpdateDep = Annotated[BookingUpdateInputSchema, Depends(BookingUpdateInputSchema)]
