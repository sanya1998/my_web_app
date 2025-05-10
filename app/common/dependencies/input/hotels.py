from typing import Annotated, List

from app.common.dependencies.input.base import BaseInput
from fastapi import Form
from pydantic import Field


class HotelBaseInput(BaseInput):
    name: str
    location: str
    services: Annotated[
        List[Annotated[str, Field(min_length=1)]],
        Field(
            description="❗️ `✅ Send empty value` => `...&services=&...`, "
            " но каждая строка из списка `services` не может быть пустой"
        ),
    ] = list()
    stars: Annotated[int | None, Field(ge=1, le=5)] = None  # TODO: все еще `integer | (integer | null)` в свагере
    image_id: int | None = None


HotelInputCreateDep = Annotated[HotelBaseInput, Form()]
HotelInputUpdateDep = Annotated[HotelBaseInput, Form()]
