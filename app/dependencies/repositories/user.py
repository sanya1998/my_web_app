from typing import Annotated

from app.dependencies.db import PostgresSessionAnn
from app.repositories import UserRepo
from fastapi import Depends


def get_user_repo(session: PostgresSessionAnn):
    return UserRepo(session=session)


UserRepoAnn = Annotated[UserRepo, Depends(get_user_repo)]
