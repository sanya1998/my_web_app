from app.common.tables.base import BaseTable
from sqlalchemy import DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import mapped_column


class QueryHistory(BaseTable):
    method = mapped_column(String, nullable=False)
    url_path = mapped_column(String, nullable=False)
    query_string = mapped_column(String, nullable=False)
    status_code = mapped_column(Integer, nullable=False)
    process_time = mapped_column(Numeric(8, 6), nullable=False)
    created_dt = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __str__(self):
        return f"QueryHistory #{self.id}"
