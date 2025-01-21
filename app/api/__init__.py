from app.api.data import data_router
from app.api.pages import pages_router
from app.api.srv import srv_router
from app.api.users import users_router
from app.common.helpers.api_version import VersionedAPIRouter

api_router = VersionedAPIRouter(is_root_router=True)

api_router.include_router(srv_router)
api_router.include_router(users_router)
api_router.include_router(data_router)
api_router.include_router(pages_router)
