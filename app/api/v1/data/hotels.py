from typing import List

from app.common.dependencies.api_args.hotels import HotelsFiltersDep
from app.common.schemas.hotel import HotelSchema
from fastapi import APIRouter

router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int) -> dict:
    return {"hotel_id": hotel_id, "hotel_name": "Hotel Name"}


@router.get("/")
async def get_hotels(search_args: HotelsFiltersDep) -> List[HotelSchema]:
    hotels = [{"hotel_id": 1, "name": "Hotel Name"}]
    return hotels
    # return [{"hotel_id": 1, "hotel_name": "Hotel Name", "date_from": date_from, "date_to": date_to}]