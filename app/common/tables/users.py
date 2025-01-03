from app.common.tables.base import BaseTable
from sqlalchemy import ARRAY, Column, String
from sqlalchemy.orm import mapped_column


class Users(BaseTable):
    email = mapped_column(String, unique=True, nullable=False)
    first_name = mapped_column(String, nullable=True)
    last_name = Column(String, nullable=True)  # TODO: mapped_column
    roles = mapped_column(
        ARRAY(String), default=list(), nullable=False
    )  # TODO: RolesEnum (jit": "off" to improve ENUM)
    hashed_password = mapped_column(String, nullable=False)

    def __str__(self):
        return f"{self.email}"
