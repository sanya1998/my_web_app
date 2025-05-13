import io

from app.common.constants.info_types import InfoTypes
from app.common.constants.paths import ALL_PATH, EXPORT_PATH, FILTERED_PATH, PATTERN_INFO_TYPE
from app.common.dependencies.auth import AdminUserDep
from app.common.dependencies.filters import ExportFiltersDep
from app.common.dependencies.services import ExportServiceDep
from app.common.exceptions.api import BaseApiError
from app.common.exceptions.services import BaseServiceError
from app.common.helpers.api_version import VersionedAPIRouter
from app.config.common import settings
from starlette.responses import StreamingResponse

router = VersionedAPIRouter(prefix=EXPORT_PATH)


def create_response(info_type: InfoTypes, stream: io.BytesIO):
    filename = f"{info_type.value}.{settings.FILE_FORMAT}"
    response = StreamingResponse(content=stream, media_type=settings.FILE_MEDIA_TYPE)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


@router.get(f"{ALL_PATH}{PATTERN_INFO_TYPE}")
async def export_all_for_admin(info_type: InfoTypes, export_service: ExportServiceDep, admin: AdminUserDep):
    try:
        stream = await export_service.export_all_in_csv()
        return create_response(info_type, stream)
    except BaseServiceError:
        raise BaseApiError


@router.get(f"{FILTERED_PATH}{PATTERN_INFO_TYPE}")
async def export_filtered_for_admin(
    info_type: InfoTypes, filters: ExportFiltersDep, export_service: ExportServiceDep, admin: AdminUserDep
):
    try:
        stream = await export_service.export_filtered_in_csv(filters)
        return create_response(info_type, stream)
    except BaseServiceError:
        raise BaseApiError
