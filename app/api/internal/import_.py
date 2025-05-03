from app.common.dependencies.auth.admin import AdminUserDep
from app.common.dependencies.services.import_ import ImportServiceDep
from app.common.exceptions.api.already_exists import AlreadyExistsApiError
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.services.already_exists import AlreadyExistsServiceError
from app.common.exceptions.services.base import BaseServiceError
from app.common.helpers.api_version import VersionedAPIRouter
from fastapi import BackgroundTasks, UploadFile

router = VersionedAPIRouter(prefix="/import")


@router.post("/all/{info_type}")
async def import_(
    background_tasks: BackgroundTasks, file: UploadFile, import_service: ImportServiceDep, admin: AdminUserDep
):
    try:
        await import_service.import_(file)
        background_tasks.add_task(file.file.close)
    except AlreadyExistsServiceError:
        raise AlreadyExistsApiError
    except BaseServiceError:
        raise BaseApiError
