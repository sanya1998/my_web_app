from typing import List

from app.common.schemas.base import BaseSchema
from fastapi import Form
from pydantic import Field


class HotelBaseSchema(BaseSchema):
    name: str
    location: str
    services: List[str] = Field(default=list())
    image_id: int | None = None


class HotelBaseInputSchema(HotelBaseSchema):
    name: str = Field(Form("Name"))
    location: str = Field(Form("Location"))
    services: List[str] = Field(Form(default=list()))
    image_id: int | None = Field(Form(None))


class HotelCreateInputSchema(HotelBaseInputSchema):
    pass


class HotelUpdateInputSchema(HotelBaseInputSchema):
    pass


class HotelUpdateSchema(HotelBaseSchema):
    pass


class HotelCreateSchema(HotelUpdateSchema):
    pass


class HotelReadSchema(HotelCreateSchema):
    id: int


class OneCreatedHotelReadSchema(HotelReadSchema):
    pass


class OneUpdatedHotelReadSchema(HotelReadSchema):
    pass


class OneHotelReadSchema(HotelReadSchema):
    pass


class OneHotelWithJoinReadSchema(HotelReadSchema):
    rooms_quantity: int  # Всего различных типов номеров


class ManyHotelsReadSchema(HotelReadSchema):
    remain_by_hotel: int


class OneDeletedHotelReadSchema(HotelReadSchema):
    pass
