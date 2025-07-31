import re

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, declared_attr, mapped_column


class BaseTable(DeclarativeBase, MappedAsDataclass):
    id = mapped_column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    created_dt = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_dt = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    @declared_attr
    def __tablename__(cls) -> str:
        # Верблюжий регистр переводится в змеиный
        return re.sub(r"([a-z])([A-Z])", r"\1_\2", cls.__name__).lower()


metadata = BaseTable.metadata
