from typing import List

from app.common.schemas.base import BaseSchema
from app.common.schemas.room import ManyRoomsReadSchema
from fastapi import Form
from pydantic import Field, model_validator


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
    remain_by_hotel: int | None = None
    rooms: List[ManyRoomsReadSchema] = Field(list(), exclude=True)  # TODO: мб поднять в родителя

    @model_validator(mode="after")
    def validate_model(self):
        if self.remain_by_hotel is None:  # TODO: нужна ли будет в дальнейшем проверка?
            self.remain_by_hotel = sum([r.remain_by_room for r in self.rooms if r.remain_by_room])
        return self


class OneDeletedHotelReadSchema(HotelReadSchema):
    pass
