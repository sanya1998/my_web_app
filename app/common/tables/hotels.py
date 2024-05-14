from app.common.tables.base import BaseTable
from sqlalchemy import JSON, Column, Integer, String


class Hotels(BaseTable):
    name = Column(String, nullable=True)
    location = Column(String, nullable=False)
    services = Column(JSON)
    rooms_quantity = Column(Integer, nullable=False)
    image_id = Column(Integer)
