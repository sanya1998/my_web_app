from app.api.internal.export import router as export_router
from app.api.internal.import_ import router as import_router
from app.common.helpers.api_version import VersionedAPIRouter

internal_router = VersionedAPIRouter(tags=["Internal"])

internal_router.include_router(import_router)
internal_router.include_router(export_router)
