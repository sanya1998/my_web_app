from typing import List

from app.common.schemas.base import BaseSchema
from fastapi import Form
from pydantic import Field


class HotelBaseInputSchema(BaseSchema):
    name: str = Field(Form())
    location: str = Field(Form())
    services: List[str] = Field(Form(default=list()))  # TODO: check default
    image_id: int | None = Field(Form(None))


class HotelBaseSchema(BaseSchema):
    name: str
    location: str
    services: List[str] = Field(default=list())
    image_id: int | None = None


class HotelBaseReadSchema(HotelBaseSchema):
    id: int


class HotelReadSchema(HotelBaseReadSchema):
    rooms_quantity: int  # Всего различных типов номеров


class ManyHotelsReadSchema(HotelBaseReadSchema):
    remain_by_hotel: int
