from app.api.v1.data import data_router
from app.api.v1.pages import pages_router
from app.api.v1.users import users_router
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(users_router)
v1_router.include_router(data_router)
v1_router.include_router(pages_router)
