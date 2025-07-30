from app.common.helpers.db import get_back_populates
from app.common.models.booking import Bookings
from app.common.models.hotel import Hotels
from app.common.models.query_history import QueryHistory
from app.common.models.room import Rooms
from app.common.models.user import Users
from sqlalchemy.orm import relationship

# TODO: минус такого подхода в том, что нет подсказок IDE для Rooms.hotel
# Rooms.hotel = relationship(Hotels, foreign_keys=Rooms.hotel_id)
# Hotels.rooms = relationship(Rooms, back_populates=get_back_populates(Rooms.hotel))
#
# Bookings.room = relationship(Rooms, foreign_keys=Bookings.room_id)
# Rooms.bookings = relationship(Bookings, back_populates=get_back_populates(Bookings.room))
#
# Bookings.user = relationship(Users, foreign_keys=Bookings.user_id)
# Users.bookings = relationship(Bookings, back_populates=get_back_populates(Bookings.user))
