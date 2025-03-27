from app.common.constants.info_types import InfoTypes
from app.common.dependencies.auth.admin import AdminUserDep
from app.common.helpers.api_version import VersionedAPIRouter

router = VersionedAPIRouter(prefix="/import")


@router.post("/{info_type}/for_admin")
async def import_(info_type: InfoTypes, admin: AdminUserDep):
    pass
