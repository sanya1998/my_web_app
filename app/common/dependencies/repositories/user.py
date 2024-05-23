from typing import Annotated

from app.common.dependencies.db.db import SessionDep
from app.repositories.user import UserRepo
from fastapi import Depends


def get_user_repo(session: SessionDep):
    return UserRepo(session=session)


UserRepoDep = Annotated[UserRepo, Depends(get_user_repo)]
