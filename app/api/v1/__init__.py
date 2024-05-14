from app.api.v1.bookings import router as router_bookings
from app.api.v1.hotels import router as router_hotels
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(router_hotels)
v1_router.include_router(router_bookings)
