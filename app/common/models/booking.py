from datetime import date
from typing import Annotated

from app.common.models.base import BaseSchema, BaseSQLModel, IdMixin
from app.common.models.room import RoomReadSchema, Rooms
from app.common.models.user import UserBaseReadSchema, Users
from pydantic import AliasChoices
from sqlalchemy import BigInteger, Column, Computed, Integer
from sqlalchemy.orm import mapped_column
from sqlmodel import Field


class BookingBaseSchema(BaseSchema):
    date_from: date  # TODO: Проверить все nullable при наследовании и не только
    date_to: date


class Bookings(BaseSQLModel, BookingBaseSchema, table=True):
    id: int = Field(sa_column=Column(BigInteger, primary_key=True, autoincrement=False))
    room_id: int = Field(foreign_key="rooms.id")
    user_id: int = Field(foreign_key="users.id")
    price: int
    # TODO: заменить константы на назв переменных
    total_days: int = Field(sa_column=Column(Integer, Computed("date_to - date_from")))  # TODO: without Integer ?
    total_cost: int = Field(sa_column=Column(Integer, Computed("(date_to - date_from) * price")))

    def __str__(self):
        return f"Booking #{self.id}"


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
    room: Annotated[RoomReadSchema, Field(schema_extra={"validation_alias": AliasChoices("room", "Rooms")})]


class BookingReadSchema(CurrentUserBookingReadSchema):
    user: Annotated[UserBaseReadSchema, Field(schema_extra={"validation_alias": AliasChoices("user", "Users")})]
