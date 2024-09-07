from app.api.v1.data.bookings import router as router_bookings
from app.api.v1.data.hotels import router as router_hotels
from app.api.v1.data.rooms import router as router_rooms
from fastapi import APIRouter

data_router = APIRouter()

data_router.include_router(router_rooms)
data_router.include_router(router_hotels)
data_router.include_router(router_bookings)
