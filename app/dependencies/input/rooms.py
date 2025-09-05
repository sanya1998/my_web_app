from typing import Annotated, List

from app.dependencies.input.base import BaseInput
from fastapi import Body


class RoomBaseInput(BaseInput):
    hotel_id: int
    name: str
    description: str | None = None
    price: int
    services: List[str] = list()
    quantity: int
    image_id: int | None = None


class RoomUpsertInput(RoomBaseInput):
    id: int | None = None


RoomInputUpsertAnn = Annotated[RoomUpsertInput, Body()]
