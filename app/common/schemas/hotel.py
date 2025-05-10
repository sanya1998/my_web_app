from typing import List

from app.common.schemas.base import BaseSchema
from pydantic import field_validator


class HotelBaseSchema(BaseSchema):
    name: str
    location: str
    services: List[str]
    stars: int | None = None
    image_id: int | None = None


class HotelBaseReadSchema(HotelBaseSchema):
    id: int


class HotelReadSchema(HotelBaseReadSchema):
    rooms_quantity: int  # Всего различных типов номеров


class ManyHotelsReadSchema(HotelBaseReadSchema):
    remain_by_hotel: int

    @field_validator("remain_by_hotel", mode="before")  # TODO: @classmethod ?
    def validate_remain_by_hotel(cls, value: int | None) -> int:
        return value if value is not None else 0
