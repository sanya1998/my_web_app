from typing import Annotated

from app.dependencies.repositories import ChosenRepo
from app.services import ImportService
from fastapi import Depends


def get_import_service(repo: ChosenRepo):
    return ImportService(repo=repo)


ImportServiceDep = Annotated[ImportService, Depends(get_import_service)]
