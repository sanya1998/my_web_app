from app.common.tables.base import BaseTable
from app.common.tables.rooms import Rooms
from app.common.tables.users import Users
from sqlalchemy import Column, Computed, Date, ForeignKey, Integer


class Bookings(BaseTable):
    room_id = Column(ForeignKey(Rooms.id), nullable=False)
    user_id = Column(ForeignKey(Users.id), nullable=False)
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    price = Column(Integer, nullable=False)
    total_days = Column(Integer, Computed("date_to - date_from"))
    total_cost = Column(Integer, Computed("(date_to - date_from) * price"))
