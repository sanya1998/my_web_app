from typing import List

from app.common.models.base import BaseSchema, BaseSQLModel, IdMixin
from pydantic import field_validator
from sqlalchemy import BigInteger, Column, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field


class HotelBaseSchema(BaseSchema):
    name: str
    location: str
    services: List[str]
    stars: int | None = None
    image_id: int | None = None


# class Hotels(BaseSQLModel, IdMixin, HotelBaseSchema, table=True):
class Hotels(BaseSQLModel, HotelBaseSchema, table=True):
    id: int = Field(sa_column=Column(BigInteger, primary_key=True, autoincrement=False))
    services: List[str] = Field(sa_column=Column(ARRAY(String), default=list()))

    def __str__(self):
        return f"Hotel #{self.id} ({self.name})"


class HotelBaseReadSchema(HotelBaseSchema):
    id: int


class HotelReadSchema(HotelBaseReadSchema):
    rooms_quantity: int  # Всего различных типов номеров


class ManyHotelsReadSchema(HotelBaseReadSchema):
    remain_by_hotel: int

    @field_validator("remain_by_hotel", mode="before")  # TODO: @classmethod ?
    def validate_remain_by_hotel(cls, value: int | None) -> int:
        return value if value is not None else 0
