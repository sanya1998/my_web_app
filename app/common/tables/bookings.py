from app.common.tables.base import BaseTable
from app.common.tables.rooms import Rooms
from app.common.tables.users import Users
from sqlalchemy import Computed, Date, ForeignKey, Integer
from sqlalchemy.orm import mapped_column


class Bookings(BaseTable):
    room_id = mapped_column(ForeignKey(Rooms.id), nullable=False)
    user_id = mapped_column(ForeignKey(Users.id), nullable=False)
    date_from = mapped_column(Date, nullable=False)
    date_to = mapped_column(Date, nullable=False)
    price = mapped_column(Integer, nullable=False)
    total_days = mapped_column(Integer, Computed("date_to - date_from"))  # TODO: заменить константы на назв переменных
    total_cost = mapped_column(Integer, Computed("(date_to - date_from) * price"))

    def __str__(self):
        return f"Booking #{self.id}"
