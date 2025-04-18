from fastapi import APIRouter

router = APIRouter()


@router.get(path="/")
def welcome() -> dict:
    """
    Приветственное сообщение
    """
    return {"message": "Welcome to the API"}
