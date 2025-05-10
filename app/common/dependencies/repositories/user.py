from typing import Annotated

from app.common.dependencies.db import PostgresSessionDep
from app.common.exceptions.api import BaseApiError
from app.common.exceptions.repositories import BaseRepoError
from app.repositories import UserRepo
from fastapi import Depends


def get_user_repo(session: PostgresSessionDep):
    try:
        return UserRepo(session=session)
    except BaseRepoError:
        raise BaseApiError


UserRepoDep = Annotated[UserRepo, Depends(get_user_repo)]
