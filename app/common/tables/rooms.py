from app.common.tables.base import BaseTable
from app.common.tables.hotels import Hotels
from sqlalchemy import ARRAY, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Rooms(BaseTable):
    hotel_id = Column(ForeignKey(Hotels.id), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    services = Column(ARRAY(String), default=list(), nullable=False)
    quantity = Column(Integer, nullable=False)
    image_id = Column(Integer, nullable=True)

    hotel = relationship(Hotels, back_populates="rooms")  # TODO: попробовать без констант
    bookings = relationship("Bookings", back_populates="room")  # TODO: попробовать без констант

    def __str__(self):
        return f"Room #{self.id} ({self.name})"
