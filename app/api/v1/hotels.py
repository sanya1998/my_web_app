from typing import List, Optional

from fastapi import APIRouter, Query, Depends
from datetime import date

from pydantic import BaseModel

router = APIRouter(prefix="/hotels", tags=["hotels"])


class SBooking(BaseModel):
    room_id: int
    date_from: date
    date_to: date


class SHotel(BaseModel):
    hotel_id: int
    name: str


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int) -> dict:
    return {"hotel_id": hotel_id, "hotel_name": "Hotel Name"}


class HotelsSearchArgs:
    def __init__(
            self,
            location: str,
            date_from: date,
            date_to: date,
            has_spa: Optional[bool] = None,
            stars: Optional[int] = Query(default=None, ge=1, le=5),
    ):
        self.location = location
        self.date_from = date_from
        self.date_to = date_to
        self.has_spa = has_spa
        self.stars = stars


@router.get("/")
async def get_hotels(
        search_args: HotelsSearchArgs = Depends()
) -> List[SHotel]:
    hotels = [{"hotel_id": 1, "name": "Hotel Name"}]
    return hotels
    # return [{"hotel_id": 1, "hotel_name": "Hotel Name", "date_from": date_from, "date_to": date_to}]


@router.post("/bookings")
def add_booking(booking: SBooking):
    pass
