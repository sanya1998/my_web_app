from typing import List

from app.common.schemas.base import BaseSchema


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
