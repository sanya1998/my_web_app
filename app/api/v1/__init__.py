from fastapi import APIRouter

from app.api.v1.hotels import router as router_hotels

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(router_hotels)
