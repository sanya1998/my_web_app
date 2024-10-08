from typing import List

from app.common.schemas.base import BaseSchema
from pydantic import Field


class RoomBaseSchema(BaseSchema):
    hotel_id: int
    name: str
    description: str | None = None
    price: int
    services: List[str] = Field(default=list())
    quantity: int
    image_id: int | None = None


class RoomCreateSchema(RoomBaseSchema):
    pass


class BaseRoomReadSchema(RoomCreateSchema):
    id: int


class OneRoomReadSchema(BaseRoomReadSchema):
    pass


class ManyRoomsReadSchema(BaseRoomReadSchema):
    # Если не указаны даты, то None, потому что невозможно посчитать
    remain_by_room: int | None = None
    total_cost: int | None = None
