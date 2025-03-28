from typing import Annotated

from app.common.dependencies.repositories.common import ChosenRepo
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.services.base import BaseServiceError
from app.services.import_ import ImportService
from fastapi import Depends


def get_import_service(repo: ChosenRepo):
    try:
        return ImportService(repo=repo)
    except BaseServiceError:
        raise BaseApiError


ImportServiceDep = Annotated[ImportService, Depends(get_import_service)]
