import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, DateTime
from sqlalchemy.orm import DeclarativeMeta, declared_attr, mapped_column
from sqlmodel import Field, SQLModel


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class BaseSQLModel(SQLModel):
    # id: int = Field(sa_column=Column(BigInteger(), primary_key=True, autoincrement=False))

    @declared_attr
    def __tablename__(cls) -> str:
        # Верблюжий регистр переводится в змеиный
        return re.sub(r"([a-z])([A-Z])", r"\1_\2", cls.__name__).lower()


# TODO: вынести в базовый класс
class IdMixin(BaseModel):
    id: int = Field(sa_column=Column(BigInteger, primary_key=True, autoincrement=False))


# TODO: вынести в базовый класс
class TimeStampMixin(BaseModel):
    # TODO: без None created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.utcnow))
    created_at: datetime | None = Field(sa_column=Column(DateTime, default=datetime.utcnow, nullable=False))
    updated_at: datetime | None = Field(sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))


metadata = BaseSQLModel.metadata
