from app.common.dependencies.auth.admin import AdminUserDep
from app.common.dependencies.filters.export import ExportFiltersDep
from app.common.dependencies.services.export import ExportServiceDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.services.base import BaseServiceError
from app.common.helpers.api_version import VersionedAPIRouter

router = VersionedAPIRouter(prefix="/export")


@router.get("/{info_type}/for_admin/filtered")
async def filtered_export(filters: ExportFiltersDep, export_service: ExportServiceDep, admin: AdminUserDep):
    """
    ! Созданный файл не принимается аналогичной ручкой import (есть проблемы с синтаксисом).
    """
    try:
        return await export_service.filtered_export_csv(filters)
    except BaseServiceError:
        raise BaseApiError


# TODO: Use filters and copy_from_query
@router.get("/{info_type}/for_admin")
async def export(export_service: ExportServiceDep, admin: AdminUserDep):
    """
    Полученный файл можно использовать в аналогичной ручке import.
    """
    try:
        return await export_service.export_csv()
    except BaseServiceError:
        raise BaseApiError
