from app.common.constants.import_ import IMPORT_RESULT, ImportResult
from app.common.constants.paths import ALL_PATH, IMPORT_PATH, PATTERN_INFO_TYPE
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.helpers.response import BaseResponse
from app.dependencies.auth import AdminUserDep
from app.dependencies.services import ImportServiceDep
from app.exceptions.api import AlreadyExistsApiError
from app.exceptions.services import AlreadyExistsServiceError
from fastapi import BackgroundTasks, UploadFile
from starlette import status

router = VersionedAPIRouter(prefix=IMPORT_PATH)


@router.post(
    f"{ALL_PATH}{PATTERN_INFO_TYPE}", response_model=BaseResponse[ImportResult], status_code=status.HTTP_201_CREATED
)
async def import_for_admin(
    background_tasks: BackgroundTasks, file: UploadFile, import_service: ImportServiceDep, admin: AdminUserDep
):
    try:
        await import_service.import_(file)
        background_tasks.add_task(file.file.close)
        return BaseResponse(content=IMPORT_RESULT)
    except AlreadyExistsServiceError:
        raise AlreadyExistsApiError
