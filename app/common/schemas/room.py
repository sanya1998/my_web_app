from typing import Annotated, List

from app.common.schemas.base import BaseSchema
from app.common.schemas.hotel import HotelBaseReadSchema
from app.common.schemas.mixins.id_created_updated import IdCreatedUpdatedMixin
from pydantic import AliasChoices, Field


class RoomBaseSchema(BaseSchema):
    hotel_id: int
    name: str
    description: str | None = None
    price: int
    services: List[str]
    quantity: int
    image_id: int | None = None


class RoomBaseReadSchema(RoomBaseSchema, IdCreatedUpdatedMixin):
    pass


class RoomReadSchema(RoomBaseReadSchema):
    hotel_id: Annotated[int | None, Field(exclude=True)] = None
    hotel: Annotated[HotelBaseReadSchema, Field(validation_alias=AliasChoices("hotel", "Hotels"))]


class ManyRoomsReadSchema(RoomReadSchema):
    remain_by_room: int
    total_cost: int  # Если не указаны даты, то 0, потому что невозможно посчитать
