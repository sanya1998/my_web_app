from app.common.tables.base import BaseTable
from sqlalchemy import ARRAY, Column, String


class Users(BaseTable):
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    roles = Column(ARRAY(String), default=list(), nullable=False)  # TODO: RolesEnum (jit": "off" to improve ENUM)
    hashed_password = Column(String, nullable=False)
