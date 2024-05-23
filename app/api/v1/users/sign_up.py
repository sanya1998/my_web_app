from app.common.dependencies.repositories.user import UserRepoDep
from app.common.schemas.user import UserInputSchema
from fastapi import APIRouter, HTTPException

sign_up_router = APIRouter()


@sign_up_router.post("/sign_up")  # , response_model=schemas.User
async def sign_up(user_data: UserInputSchema, user_repo: UserRepoDep):
    user = await user_repo.get_object(email=user_data.email)
    if user:
        raise HTTPException(409)
        # TODO: raise AlreadyExistsError

    user = await user_repo.create(user_data)
    return user
