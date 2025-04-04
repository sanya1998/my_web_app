from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, declared_attr, mapped_column


class BaseTable(DeclarativeBase):
    id = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


metadata = BaseTable.metadata
