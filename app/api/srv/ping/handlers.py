from app.common.constants.paths import PING_PATH
from app.common.constants.srv import PING_RESULT_V1, PING_RESULT_V2, PingResult
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.helpers.response import BaseResponse
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

router = VersionedAPIRouter()


@router.get(path=PING_PATH, response_model=BaseResponse[PingResult], deprecated=True)
async def ping():
    """
    Проверяет доступность api v1
    """
    return JSONResponse(content=jsonable_encoder(BaseResponse(content=PING_RESULT_V1)))


@router.get(path=PING_PATH, response_model=BaseResponse[PingResult])
@router.set_api_version("v2")
async def ping():  # noqa: F811 (Игнорировать повторное определение ping)
    """
    Проверяет доступность api v2
    """
    return BaseResponse(content=PING_RESULT_V2)
