from sqlalchemy import JSON, Column, Integer, String

from app.common.tables.base import BaseTable


class Hotels(BaseTable):
    name = Column(String, nullable=True)
    location = Column(String, nullable=False)
    services = Column(JSON)
    rooms_quantity = Column(Integer, nullable=False)
    image_id = Column(Integer)
