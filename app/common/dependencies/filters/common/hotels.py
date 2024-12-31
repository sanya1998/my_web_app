from app.common.dependencies.filters.base import BaseFilters
from app.common.tables import Hotels


class HotelBaseFilters(BaseFilters):
    _db_model = Hotels
    name: str | None = None
    location: str | None = None  # TODO: search, not ==
