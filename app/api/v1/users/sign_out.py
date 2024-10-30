from app.common.dependencies.services.authorization import AuthorizationServiceDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.services.base import BaseServiceError
from fastapi import APIRouter

sign_out_router = APIRouter()


@sign_out_router.post("/sign_out")
async def sign_out(auth_service: AuthorizationServiceDep) -> None:
    try:
        await auth_service.sign_out()
    except BaseServiceError:
        raise BaseApiError
