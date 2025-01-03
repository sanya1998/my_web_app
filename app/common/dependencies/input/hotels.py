from typing import Annotated, List

from app.common.dependencies.input.base import BaseInput
from fastapi import Depends, Form
from pydantic import Field


class HotelBaseInput(BaseInput):
    name: str = Field(Form())
    location: str = Field(Form())
    services: List[str] = Field(Form(default=list()))
    stars: int | None = Field(Form(None))
    image_id: int | None = Field(Form(None))


HotelInputCreateDep = Annotated[HotelBaseInput, Depends(HotelBaseInput)]
HotelInputUpdateDep = Annotated[HotelBaseInput, Depends(HotelBaseInput)]
