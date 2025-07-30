from app.common.models.query_history import QueryHistoryBaseSchema, QueryHistoryReadSchema
from app.common.tables import QueryHistory
from app.repositories.base import BaseRepository


class QueryHistoryRepo(BaseRepository):
    db_model = QueryHistory

    one_created_read_schema = QueryHistoryReadSchema

    create_schema = QueryHistoryBaseSchema
