from sqlalchemy import Column, String

from app.common.tables.base import BaseTable


class Users(BaseTable):
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
