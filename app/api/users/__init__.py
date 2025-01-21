from app.api.users.get import get_router
from app.api.users.sign_in import sign_in_router
from app.api.users.sign_out import sign_out_router
from app.api.users.sign_up import sign_up_router
from app.common.helpers.api_version import VersionedAPIRouter

users_router = VersionedAPIRouter(prefix="/users", tags=["Users"])

users_router.include_router(sign_up_router)
users_router.include_router(sign_in_router)
users_router.include_router(sign_out_router)
users_router.include_router(get_router)
