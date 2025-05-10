from app.common.dependencies.auth import AdminUserDep
from app.common.dependencies.services import ImportServiceDep
from app.common.exceptions.api import AlreadyExistsApiError, BaseApiError
from app.common.exceptions.services import AlreadyExistsServiceError, BaseServiceError
from app.common.helpers.api_version import VersionedAPIRouter
from fastapi import BackgroundTasks, UploadFile

router = VersionedAPIRouter(prefix="/import")


@router.post("/all/{info_type}")
async def import_for_admin(
    background_tasks: BackgroundTasks, file: UploadFile, import_service: ImportServiceDep, admin: AdminUserDep
):
    try:
        await import_service.import_(file)
        background_tasks.add_task(file.file.close)
    except AlreadyExistsServiceError:
        raise AlreadyExistsApiError
    except BaseServiceError:
        raise BaseApiError
