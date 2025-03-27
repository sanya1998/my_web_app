from app.common.dependencies.auth.admin import AdminUserDep
from app.common.dependencies.filters.export import ExportFiltersDep
from app.common.dependencies.services.export import ExportServiceDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.services.base import BaseServiceError
from app.common.helpers.api_version import VersionedAPIRouter

router = VersionedAPIRouter(prefix="/export")


@router.get("/{info_type}/for_admin")
async def export(filters: ExportFiltersDep, export_service: ExportServiceDep, admin: AdminUserDep):
    try:
        return await export_service.export_csv(filters)
    except BaseServiceError:
        raise BaseApiError
