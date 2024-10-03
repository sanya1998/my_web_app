from app.api.v1.users.get import get_router
from app.api.v1.users.sign_in import sign_in_router
from app.api.v1.users.sign_out import sign_out_router
from app.api.v1.users.sign_up import sign_up_router
from fastapi import APIRouter

users_router = APIRouter(prefix="/users", tags=["Users"])

users_router.include_router(sign_up_router)
users_router.include_router(sign_in_router)
users_router.include_router(sign_out_router)
users_router.include_router(get_router)
