from typing import Annotated

from app.dependencies.db import PostgresSessionDep
from app.repositories import UserRepo
from fastapi import Depends


def get_user_repo(session: PostgresSessionDep):
    return UserRepo(session=session)


UserRepoDep = Annotated[UserRepo, Depends(get_user_repo)]
