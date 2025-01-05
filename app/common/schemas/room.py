from typing import List

from app.common.schemas.base import BaseSchema
from app.common.schemas.hotel import HotelBaseReadSchema
from pydantic import AliasChoices, Field


class RoomBaseSchema(BaseSchema):
    hotel_id: int
    name: str
    description: str | None = None
    price: int
    services: List[str] = Field(default=list())
    quantity: int
    image_id: int | None = None


class RoomBaseReadSchema(RoomBaseSchema):
    id: int


class RoomReadSchema(RoomBaseReadSchema):
    hotel_id: int | None = Field(None, exclude=True)
    hotel: HotelBaseReadSchema = Field(validation_alias=AliasChoices("hotel", "Hotels"))


class ManyRoomsReadSchema(RoomReadSchema):
    remain_by_room: int
    # Если не указаны даты, то 0, потому что невозможно посчитать
    total_cost: int
