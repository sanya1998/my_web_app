from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.api_models.base import BaseModel
from app.common.exceptions.repositories.base import BaseNotFound
from app.common.tables.base import BaseTable


class BaseRepository:
    db_model: BaseTable
    schema_model: BaseModel
    exception_not_found: BaseNotFound

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_objects(self, filters):
        query = select(self.db_model)
        result = await self.session.execute(query)
        bookings = result.scalars().all()
        # TODO: work with limit and offset + max_limit (env)
        return bookings

    async def get_object(self, object_id):
        query = select(self.db_model).where(self.db_model.id == object_id)
        result = await self.session.execute(query)
        try:
            booking = result.scalar_one()
        except NoResultFound:
            raise self.exception_not_found
        return self.schema_model.from_orm(booking)

    async def create(self, data):
        raise NotImplementedError

    async def upsert(self, data):
        raise NotImplementedError

    async def update_object(self, object_id, data):
        raise NotImplementedError

    async def update_object_field(self, object_id, data):
        raise NotImplementedError

    async def delete(self, object_id):
        raise NotImplementedError
