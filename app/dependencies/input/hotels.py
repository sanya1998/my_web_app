from typing import Annotated, List

from app.dependencies.input.base import BaseInput
from fastapi import Body, Form
from pydantic import Field


class HotelBaseInput(BaseInput):
    name: str | None = None
    location: str | None = None
    services: Annotated[
        List[Annotated[str, Field(min_length=1)]],
        Field(
            description="❗️ `✅ Send empty value` => `...&services=&...`, "
            " но каждая строка из списка `services` не может быть пустой"
        ),
    ] = list()
    stars: Annotated[int | None, Field(ge=1, le=5)] = None  # TODO: все еще `integer | (integer | null)` в свагере
    image_id: int | None = None


class HotelUpsertInput(HotelBaseInput):
    name: str
    location: str


HotelInputPatchAnn = Annotated[HotelBaseInput, Body()]
HotelInputCreateAnn = Annotated[HotelUpsertInput, Form()]
HotelInputUpdateAnn = Annotated[HotelUpsertInput, Body()]
