from typing import Annotated

from app.common.dependencies.db.postgres import PostgresSessionDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.repositories.user import UserRepo
from fastapi import Depends


def get_user_repo(session: PostgresSessionDep):
    try:
        return UserRepo(session=session)
    except BaseRepoError:
        raise BaseApiError


UserRepoDep = Annotated[UserRepo, Depends(get_user_repo)]
