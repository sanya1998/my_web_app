from app.common.tables.base import BaseTable
from sqlalchemy import ARRAY, Column, Integer, String


class Hotels(BaseTable):
    name = Column(String, nullable=True)
    location = Column(String, nullable=False)
    services = Column(ARRAY(String), nullable=False)
    rooms_quantity = Column(Integer, nullable=False)
    image_id = Column(Integer)
