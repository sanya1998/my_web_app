from app.api.srv.ping import router as ping_router
from app.api.srv.welcome import router as welcome_router
from fastapi import APIRouter

srv_router = APIRouter(tags=["system"])

srv_router.include_router(welcome_router)
srv_router.include_router(ping_router)
