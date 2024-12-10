from app.common.tables.base import BaseTable
from sqlalchemy import ARRAY, Integer, String
from sqlalchemy.orm import mapped_column


class Hotels(BaseTable):
    name = mapped_column(String, nullable=False)
    location = mapped_column(String, nullable=False)
    services = mapped_column(ARRAY(String), default=list(), nullable=False)
    image_id = mapped_column(Integer, nullable=True)

    def __str__(self):
        return f"Hotel #{self.id} ({self.name})"
