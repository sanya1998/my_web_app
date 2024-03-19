from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):

    # Generate __tablename__
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
