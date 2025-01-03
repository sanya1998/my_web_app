from typing import Annotated

from app.common.schemas.hotel import HotelBaseInputSchema
from fastapi import Depends

HotelInputCreateDep = Annotated[HotelBaseInputSchema, Depends(HotelBaseInputSchema)]
HotelInputUpdateDep = Annotated[HotelBaseInputSchema, Depends(HotelBaseInputSchema)]
