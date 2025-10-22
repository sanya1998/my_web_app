from app.api import auth, data, frontend, internal, media, srv, users
from app.common.constants.paths import ROOT_API_PATH
from app.common.helpers.api_version import VersionedAPIRouter

api_router = VersionedAPIRouter(prefix=ROOT_API_PATH, is_root_router=True)

api_router.include_router(srv.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(data.router)
api_router.include_router(media.router)
api_router.include_router(frontend.router)
api_router.include_router(internal.router)
