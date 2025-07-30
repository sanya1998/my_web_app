import re

from sqlalchemy import BigInteger
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, declared_attr, mapped_column


class BaseTable(DeclarativeBase, MappedAsDataclass):
    id = mapped_column(BigInteger, primary_key=True, nullable=False, autoincrement=True)

    @declared_attr
    def __tablename__(cls) -> str:
        # Верблюжий регистр переводится в змеиный
        return re.sub(r"([a-z])([A-Z])", r"\1_\2", cls.__name__).lower()


metadata = BaseTable.metadata
