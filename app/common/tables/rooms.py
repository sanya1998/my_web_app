from app.common.tables.base import BaseTable
from app.common.tables.hotels import Hotels
from sqlalchemy import ARRAY, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column


class Rooms(BaseTable):
    hotel_id = mapped_column(ForeignKey(Hotels.id), nullable=False)
    name = mapped_column(String, nullable=False)
    description = mapped_column(String, nullable=True)
    price = mapped_column(Integer, nullable=False)
    services = mapped_column(ARRAY(String), default=list(), nullable=False)
    quantity = mapped_column(Integer, nullable=False)
    image_id = mapped_column(Integer, nullable=True)

    def __str__(self):
        return f"Room #{self.id} ({self.name})"
