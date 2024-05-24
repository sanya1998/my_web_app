from app.common.schemas.user import UserCreateSchema, UserInputSchema, UserReadSchema
from app.common.tables import Users
from app.repositories.base import BaseRepository


class UserRepo(BaseRepository):
    db_model = Users

    read_schema = UserReadSchema
    create_schema = UserCreateSchema

    async def create(self, raw_data: UserInputSchema) -> read_schema:
        data = self.create_schema.model_validate(raw_data)
        return await super().create(data)
