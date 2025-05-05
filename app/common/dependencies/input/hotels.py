from typing import Annotated, List

from app.common.dependencies.input.base import BaseInput
from fastapi import Body, Form


class HotelBaseInput(BaseInput):
    name: str
    location: str
    services: Annotated[List[str], Body(default=list())]  # TODO pycharm подчеркивает list()
    stars: Annotated[int | None, Body(ge=1, le=5)] = None  # TODO: все еще `integer | (integer | null)` в свагере
    image_id: int | None = None


HotelInputCreateDep = Annotated[HotelBaseInput, Form()]
HotelInputUpdateDep = Annotated[HotelBaseInput, Form()]
