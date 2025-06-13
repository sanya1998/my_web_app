from datetime import datetime

from app.common.schemas.base import BaseSchema


class QueryHistoryBaseSchema(BaseSchema):
    method: str
    url_path: str
    query_string: str
    status_code: int
    process_time: float


class QueryHistoryReadSchema(QueryHistoryBaseSchema):
    id: int
    created_dt: datetime
