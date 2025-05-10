from app.api.srv.ping import router as ping_router
from app.api.srv.tmp import router as testing_router
from app.api.srv.welcome import router as welcome_router
from app.common.helpers.api_version import VersionedAPIRouter

srv_router = VersionedAPIRouter(tags=["System"])

srv_router.include_router(welcome_router)
srv_router.include_router(ping_router)
srv_router.include_router(testing_router)
