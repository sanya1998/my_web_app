from fastapi import APIRouter

router = APIRouter()


@router.get(path="/ping")
async def ping() -> dict:
    """
    Проверяет доступность
    """
    return {"success": True}
