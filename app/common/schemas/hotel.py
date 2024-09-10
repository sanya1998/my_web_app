from typing import List

from app.common.schemas.base import BaseSchema
from pydantic import Field


class HotelBaseSchema(BaseSchema):
    name: str
    location: str
    services: List[str] = Field(default=list())
    image_id: int | None = None


class HotelCreateSchema(HotelBaseSchema):
    pass


class HotelReadSchema(HotelCreateSchema):
    id: int


class OneHotelReadSchema(HotelReadSchema):
    pass


class ManyHotelsReadSchema(HotelReadSchema):
    remain_by_hotel: int | None = None  # Если не указаны даты, то None, потому что невозможно посчитать
