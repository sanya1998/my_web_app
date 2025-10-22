from app.api.media import images
from app.common.constants.paths import MEDIA_PATH
from app.common.constants.tags import TagsEnum
from app.common.helpers.api_version import VersionedAPIRouter

router = VersionedAPIRouter(prefix=MEDIA_PATH, tags=[TagsEnum.MEDIA])
router.include_router(images.router)
