from app.api.media.images import router_images
from app.common.constants.paths import MEDIA_PATH
from app.common.constants.tags import TagsEnum
from app.common.helpers.api_version import VersionedAPIRouter

media_router = VersionedAPIRouter(prefix=MEDIA_PATH, tags=[TagsEnum.MEDIA])
media_router.include_router(router_images)
