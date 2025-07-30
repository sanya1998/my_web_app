from typing import Annotated, List

from app.common.models.base import BaseSchema, BaseSQLModel, IdMixin
from app.common.models.hotel import HotelBaseReadSchema, Hotels
from pydantic import AliasChoices
from sqlalchemy import BigInteger, Column, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field


class RoomBaseSchema(BaseSchema):
    hotel_id: int
    name: str
    description: str | None = None
    price: int
    services: List[str]
    quantity: int
    image_id: int | None = None


class Rooms(BaseSQLModel, RoomBaseSchema, table=True):
    id: int = Field(sa_column=Column(BigInteger, primary_key=True, autoincrement=False))
    hotel_id: int = Field(foreign_key="hotels.id")
    services: List[str] = Field(sa_column=Column(ARRAY(String), default=list()))

    def __str__(self):
        return f"Room #{self.id} ({self.name})"


class RoomBaseReadSchema(RoomBaseSchema):
    id: int


class RoomReadSchema(RoomBaseReadSchema):
    hotel_id: Annotated[int | None, Field(exclude=True)] = None
    hotel: Annotated[HotelBaseReadSchema, Field(schema_extra={"validation_alias": AliasChoices("hotel", "Hotels")})]


class ManyRoomsReadSchema(RoomReadSchema):
    remain_by_room: int
    # Если не указаны даты, то 0, потому что невозможно посчитать
    total_cost: int
