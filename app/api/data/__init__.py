from app.api.data.bookings import router_bookings
from app.api.data.hotels import router_hotels
from app.api.data.rooms import router_rooms
from app.common.helpers.api_version import VersionedAPIRouter

data_router = VersionedAPIRouter()

data_router.include_router(router_rooms)
data_router.include_router(router_hotels)
data_router.include_router(router_bookings)
