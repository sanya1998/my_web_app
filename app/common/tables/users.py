from app.common.tables.base import BaseTable
from sqlalchemy import ARRAY, Column, String


class Users(BaseTable):
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    roles = Column(ARRAY(String), default=[], nullable=False)  # TODO: RolesEnum
    hashed_password = Column(String, nullable=False)
