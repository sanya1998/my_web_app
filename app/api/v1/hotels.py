from fastapi import APIRouter

router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int) -> dict:
    return {"hotel_id": hotel_id, "hotel_name": "Hotel Name"}


