from app.common.tables import Hotels
from app.dependencies.filters.base import BaseFilters


class HotelBaseFilters(BaseFilters):
    _db_model = Hotels
    name: str | None = None
    location: str | None = None
