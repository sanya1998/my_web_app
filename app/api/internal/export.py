import io

from app.common.constants.info_types import InfoTypes
from app.common.dependencies.auth.admin import AdminUserDep
from app.common.dependencies.filters.export import ExportFiltersDep
from app.common.dependencies.services.export import ExportServiceDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.services.base import BaseServiceError
from app.common.helpers.api_version import VersionedAPIRouter
from app.config.common import settings
from starlette.responses import StreamingResponse

router = VersionedAPIRouter(prefix="/export")


def create_response(info_type: InfoTypes, stream: io.BytesIO):
    filename = f"{info_type.value}.{settings.FILE_FORMAT}"
    response = StreamingResponse(content=stream, media_type=settings.FILE_MEDIA_TYPE)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


@router.get("/all/{info_type}/for_admin")
async def export_all(info_type: InfoTypes, export_service: ExportServiceDep, admin: AdminUserDep):
    try:
        stream = await export_service.export_all_in_csv()
        return create_response(info_type, stream)
    except BaseServiceError:
        raise BaseApiError


@router.get("/filtered/{info_type}/for_admin")
async def export_filtered(
    info_type: InfoTypes, filters: ExportFiltersDep, export_service: ExportServiceDep, admin: AdminUserDep
):
    try:
        stream = await export_service.export_filtered_in_csv(filters)
        return create_response(info_type, stream)
    except BaseServiceError:
        raise BaseApiError
