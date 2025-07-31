from app.common.schemas.base import BaseSchema
from app.common.schemas.mixins.id_created_updated import IdCreatedUpdatedMixin


class QueryHistoryBaseSchema(BaseSchema):
    method: str
    url_path: str
    query_string: str
    status_code: int
    process_time: float


class QueryHistoryReadSchema(QueryHistoryBaseSchema, IdCreatedUpdatedMixin):
    pass
