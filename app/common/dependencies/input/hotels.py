from typing import Annotated

from app.common.schemas.hotel import HotelCreateInputSchema, HotelUpdateInputSchema
from fastapi import Depends

HotelInputCreateDep = Annotated[HotelCreateInputSchema, Depends(HotelCreateInputSchema)]
HotelInputUpdateDep = Annotated[HotelUpdateInputSchema, Depends(HotelUpdateInputSchema)]
