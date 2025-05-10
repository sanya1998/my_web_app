from app.common.constants.srv import PING_V1, PING_V2
from app.common.helpers.api_version import VersionedAPIRouter

router = VersionedAPIRouter()


@router.get(path="/ping")
async def ping() -> dict:
    """
    Проверяет доступность api v1
    """
    return PING_V1


@router.get(path="/ping")
@router.set_api_version("v2")
async def ping() -> dict:  # noqa: F811 (Игнорировать повторное определение ping)
    """
    Проверяет доступность api v2
    """
    return PING_V2
