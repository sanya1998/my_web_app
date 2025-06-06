from app.api.internal.export import router as export_router
from app.api.internal.import_ import router as import_router
from app.common.constants.tags import TagsEnum
from app.common.helpers.api_version import VersionedAPIRouter
from app.dependencies.auth.roles.admin import AdminDep

internal_router = VersionedAPIRouter(tags=[TagsEnum.INTERNAL], dependencies=[AdminDep])

internal_router.include_router(import_router)
internal_router.include_router(export_router)
