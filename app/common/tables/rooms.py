from sqlalchemy import Integer, Column, ForeignKey, String, JSON

from app.common.tables.base import Base
from app.common.tables.hotels import Hotels


class Rooms(Base):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    hotel_id = Column(ForeignKey(Hotels.id), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    services = Column(JSON, nullable=True)
    quantity = Column(Integer, nullable=False)
    image_id = Column(Integer)


