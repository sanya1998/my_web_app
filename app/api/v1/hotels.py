from typing import List, Optional

from fastapi import APIRouter, Query
from datetime import date

from pydantic import BaseModel

router = APIRouter(prefix="/hotels", tags=["hotels"])


class SBooking(BaseModel):
    room_id: int
    date_from: date
    date_to: date


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int) -> dict:
    return {"hotel_id": hotel_id, "hotel_name": "Hotel Name"}


@router.get("/")
async def get_hotels(
        location: str,
        date_from: date,
        date_to: date,
        has_spa: Optional[bool] = None,
        stars: Optional[int] = Query(default=None, ge=1, le=5),
) -> List[dict]:
    return [{"hotel_id": 1, "hotel_name": "Hotel Name", "date_from": date_from, "date_to": date_to}]


@router.post("/bookings")
def add_booking(booking: SBooking):
    pass
