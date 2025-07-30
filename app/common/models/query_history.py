from datetime import datetime

from app.common.models.base import BaseSchema, BaseSQLModel, IdMixin
from sqlalchemy import BigInteger, Column, DateTime, Numeric, func
from sqlmodel import Field


class QueryHistoryBaseSchema(BaseSchema):
    method: str
    url_path: str
    query_string: str
    status_code: int
    process_time: float


class QueryHistory(BaseSQLModel, QueryHistoryBaseSchema, table=True):
    id: int = Field(sa_column=Column(BigInteger, primary_key=True, autoincrement=False))
    process_time: float = Field(sa_column=Column(Numeric(8, 6)))  # Field(default=0, max_digits=8, decimal_places=6)
    created_dt: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))

    def __str__(self):
        return f"QueryHistory #{self.id}"


# TODO: try QueryHistoryReadSchema(QueryHistory). И проверить то же самое в других моделях
class QueryHistoryReadSchema(QueryHistoryBaseSchema):
    id: int
    created_dt: datetime
