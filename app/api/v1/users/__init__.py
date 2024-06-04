from app.api.v1.users.sign_in import sign_in_router
from app.api.v1.users.sign_up import sign_up_router
from fastapi import APIRouter

users_router = APIRouter(prefix="/users", tags=["users"])

users_router.include_router(sign_up_router)
users_router.include_router(sign_in_router)
