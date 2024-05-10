from sqlalchemy import JSON, Column, ForeignKey, Integer, String

from app.common.tables.base import BaseTable
from app.common.tables.hotels import Hotels


class Rooms(BaseTable):
    hotel_id = Column(ForeignKey(Hotels.id), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    services = Column(JSON, nullable=True)
    quantity = Column(Integer, nullable=False)
    image_id = Column(Integer)
