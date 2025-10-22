from app.api.srv import ping, tmp, welcome
from app.common.constants.tags import TagsEnum
from app.common.helpers.api_version import VersionedAPIRouter

router = VersionedAPIRouter(tags=[TagsEnum.SRV])

router.include_router(welcome.router)
router.include_router(ping.router)
router.include_router(tmp.router)
