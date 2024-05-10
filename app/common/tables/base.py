from sqlalchemy import Column, Integer
from sqlalchemy.orm import DeclarativeBase, declared_attr


class BaseTable(DeclarativeBase):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)

    # Generate __tablename__
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


metadata = BaseTable.metadata
