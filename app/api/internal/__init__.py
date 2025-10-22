from app.api.internal import export, import_
from app.common.constants.tags import TagsEnum
from app.common.helpers.api_version import VersionedAPIRouter
from app.dependencies.auth.roles.admin import AdminDep

router = VersionedAPIRouter(tags=[TagsEnum.INTERNAL], dependencies=[AdminDep])

router.include_router(import_.router)
router.include_router(export.router)
