from app.api.frontend import pages, sse
from app.common.constants.tags import TagsEnum
from app.common.helpers.api_version import VersionedAPIRouter

router = VersionedAPIRouter(tags=[TagsEnum.FRONTEND])
router.include_router(pages.router)
router.include_router(sse.router)
