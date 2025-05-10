from app.api.users.handlers import router
from app.common.helpers.api_version import VersionedAPIRouter

users_router = VersionedAPIRouter(prefix="/users", tags=["Users"])

users_router.include_router(router)
