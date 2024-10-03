from app.api.v1.pages.handler import router
from fastapi import APIRouter

pages_router = APIRouter()

pages_router.include_router(router)
