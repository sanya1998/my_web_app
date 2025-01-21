from app.common.helpers.api_version import VersionedAPIRouter

router = VersionedAPIRouter()


@router.get(path="/ping")
async def ping() -> dict:
    """
    Проверяет доступность
    """
    return {"api_version": 1, "success": True}


@router.get(path="/ping")
@router.set_api_version("v2")
async def ping() -> dict:  # noqa: F811 (Игнорировать повторное определение ping)
    """
    Проверяет доступность
    """
    return {"api_version": 2, "success": True}
