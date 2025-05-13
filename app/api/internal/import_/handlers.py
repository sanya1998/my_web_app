from app.common.constants.import_ import IMPORT_RESULT, ImportResult
from app.common.constants.paths import ALL_PATH, IMPORT_PATH, PATTERN_INFO_TYPE
from app.common.dependencies.auth import AdminUserDep
from app.common.dependencies.services import ImportServiceDep
from app.common.exceptions.api import AlreadyExistsApiError, BaseApiError
from app.common.exceptions.services import AlreadyExistsServiceError, BaseServiceError
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.helpers.response import BaseResponse
from fastapi import BackgroundTasks, UploadFile

router = VersionedAPIRouter(prefix=IMPORT_PATH)


@router.post(f"{ALL_PATH}{PATTERN_INFO_TYPE}", response_model=BaseResponse[ImportResult])
async def import_for_admin(
    background_tasks: BackgroundTasks, file: UploadFile, import_service: ImportServiceDep, admin: AdminUserDep
):
    try:
        await import_service.import_(file)
        background_tasks.add_task(file.file.close)
        return BaseResponse(content=IMPORT_RESULT)
    except AlreadyExistsServiceError:
        raise AlreadyExistsApiError
    except BaseServiceError:
        raise BaseApiError
