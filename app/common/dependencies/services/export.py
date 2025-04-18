from typing import Annotated

from app.common.dependencies.repositories.common import ChosenRepo
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.services.base import BaseServiceError
from app.services.export import ExportService
from fastapi import Depends


def get_export_service(repo: ChosenRepo):
    try:
        return ExportService(repo=repo)
    except BaseServiceError:
        raise BaseApiError


ExportServiceDep = Annotated[ExportService, Depends(get_export_service)]
