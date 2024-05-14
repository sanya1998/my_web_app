from app.common.tables.base import BaseTable
from sqlalchemy import Column, String


class Users(BaseTable):
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
