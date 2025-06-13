from app.common.helpers.db import get_back_populates
from app.common.tables.bookings import Bookings
from app.common.tables.hotels import Hotels
from app.common.tables.query_history import QueryHistory
from app.common.tables.rooms import Rooms
from app.common.tables.users import Users
from sqlalchemy.orm import relationship

Rooms.hotel = relationship(Hotels, foreign_keys=Rooms.hotel_id)
Hotels.rooms = relationship(Rooms, back_populates=get_back_populates(Rooms.hotel))

Bookings.room = relationship(Rooms, foreign_keys=Bookings.room_id)
Rooms.bookings = relationship(Bookings, back_populates=get_back_populates(Bookings.room))

Bookings.user = relationship(Users, foreign_keys=Bookings.user_id)
Users.bookings = relationship(Bookings, back_populates=get_back_populates(Bookings.user))
