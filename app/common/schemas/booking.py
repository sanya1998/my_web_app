from datetime import date, timedelta

from app.common.schemas.base import BaseSchema
from fastapi import Form
from pydantic import Field


class BookingSchemaBase(BaseSchema):
    room_id: int
    date_from: date
    date_to: date


class BookingInputSchema(BookingSchemaBase):
    room_id: int = Field(Form(1))
    date_from: date = Field(Form(date.today()))
    date_to: date = Field(Form(date.today() + timedelta(days=1)))


class BookingCreateSchema(BookingSchemaBase):
    price: int
    user_id: int


class BookingReadSchema(BookingCreateSchema):
    id: int
    total_days: int
    total_cost: int
