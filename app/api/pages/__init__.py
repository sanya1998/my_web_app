from app.api.pages.handler import router
from app.common.helpers.api_version import VersionedAPIRouter

pages_router = VersionedAPIRouter()

pages_router.include_router(router)
