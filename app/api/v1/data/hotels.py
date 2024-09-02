from typing import List

from app.common.dependencies.filters.hotels import HotelsFiltersDep
from app.common.schemas.hotel import HotelSchema
from fastapi import APIRouter

router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int) -> dict:
    # TODO: получать из бд, по аналогии с bookings
    return {"hotel_id": hotel_id, "hotel_name": "Hotel Name"}


@router.get("/")
async def get_hotels(search_args: HotelsFiltersDep) -> List[HotelSchema]:
    # TODO: получать из бд, по аналогии с bookings
    hotels = [{"hotel_id": 1, "name": "Hotel Name"}]
    return hotels
    # return [{"hotel_id": 1, "hotel_name": "Hotel Name", "date_from": date_from, "date_to": date_to}]
