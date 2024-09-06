from app.common.tables.base import BaseTable
from sqlalchemy import ARRAY, Column, Integer, String


class Hotels(BaseTable):
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    services = Column(ARRAY(String), default=list(), nullable=False)
    image_id = Column(Integer, nullable=True)
