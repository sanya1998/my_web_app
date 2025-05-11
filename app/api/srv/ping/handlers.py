from app.common.constants.api import PING_PATH
from app.common.constants.srv import PING_RESULT_V1, PING_RESULT_V2
from app.common.helpers.api_version import VersionedAPIRouter

router = VersionedAPIRouter()


@router.get(path=PING_PATH)
async def ping() -> dict:
    """
    Проверяет доступность api v1
    """
    return PING_RESULT_V1


@router.get(path=PING_PATH)
@router.set_api_version("v2")
async def ping() -> dict:  # noqa: F811 (Игнорировать повторное определение ping)
    """
    Проверяет доступность api v2
    """
    return PING_RESULT_V2
