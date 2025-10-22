from app.api.data import bookings, hotels, rooms
from app.common.helpers.api_version import VersionedAPIRouter

router = VersionedAPIRouter()

router.include_router(hotels.router)
router.include_router(rooms.router)
router.include_router(bookings.router)
