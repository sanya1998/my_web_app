from fastapi import APIRouter

router = APIRouter()


@router.get(path="/")
def welcome() -> dict:
    """
    Приветственное сообщение
    """
    # TODO: HTMLResponse
    return {"message": "Welcome to the API"}
