from typing import Annotated

from app.dependencies.repositories.common import ChosenRepo
from app.services import ExportService
from fastapi import Depends


def get_export_service(repo: ChosenRepo):
    return ExportService(repo=repo)


ExportServiceAnn = Annotated[ExportService, Depends(get_export_service)]
