from app.common.tables.base import BaseTable
from sqlalchemy import ARRAY, Column, Integer, String
from sqlalchemy.orm import relationship


class Hotels(BaseTable):
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    services = Column(ARRAY(String), default=list(), nullable=False)
    image_id = Column(Integer, nullable=True)

    rooms = relationship("Rooms", back_populates="hotel")  # TODO: попробовать без констант

    def __str__(self):
        return f"Hotel #{self.id} ({self.name})"
