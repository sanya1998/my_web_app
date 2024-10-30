from app.common.tables.base import BaseTable
from sqlalchemy import ARRAY, Column, String
from sqlalchemy.orm import relationship


class Users(BaseTable):
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    roles = Column(ARRAY(String), default=list(), nullable=False)  # TODO: RolesEnum (jit": "off" to improve ENUM)
    hashed_password = Column(String, nullable=False)

    bookings = relationship("Bookings", back_populates="user")  # TODO: попробовать без констант

    def __str__(self):
        return f"{self.email}"
