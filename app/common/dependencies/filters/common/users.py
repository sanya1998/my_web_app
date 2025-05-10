from app.common.dependencies.filters.base import BaseFilters
from app.common.tables import Users


class UserBaseFilters(BaseFilters):
    _db_model = Users
    id: int | None = None
    email: str | None = None
