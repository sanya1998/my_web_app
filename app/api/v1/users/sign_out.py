from app.common.dependencies.services.authorization import AuthorizationServiceDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.services.base import BaseServiceError
from fastapi import APIRouter, Response

sign_out_router = APIRouter()


@sign_out_router.post("/sign_out")
async def sign_out(auth_service: AuthorizationServiceDep, response: Response):
    try:
        await auth_service.sign_out(response)
    except BaseServiceError:
        raise BaseApiError
