from typing import Annotated

from app.common.dependencies.api_args.base import BaseFilterSchema
from fastapi import Depends
from pydantic import computed_field


class BookingsFilterSchema(BaseFilterSchema):
    room_id: int | None = None
    user_id: int | None = None
    price_min: int | None = None
    price_max: int | None = None

    @computed_field
    @property
    def price(self) -> tuple[int | None, int | None]:
        return self.price_min, self.price_max


BookingsFiltersDep = Annotated[BookingsFilterSchema, Depends(BookingsFilterSchema)]
