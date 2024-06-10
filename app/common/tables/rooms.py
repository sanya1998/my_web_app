from app.common.tables.base import BaseTable
from app.common.tables.hotels import Hotels
from sqlalchemy import ARRAY, Column, ForeignKey, Integer, String


class Rooms(BaseTable):
    hotel_id = Column(ForeignKey(Hotels.id), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    services = Column(ARRAY(String), nullable=False)
    quantity = Column(Integer, nullable=False)
    image_id = Column(Integer)
