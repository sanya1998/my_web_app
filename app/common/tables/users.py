from sqlalchemy import Integer, Column, String

from app.common.tables.base import Base


class Users(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
