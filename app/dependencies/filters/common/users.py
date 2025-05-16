from app.common.tables import Users
from app.dependencies.filters.base import BaseFilters


class UserBaseFilters(BaseFilters):
    _db_model = Users
    id: int | None = None
    email: str | None = None
