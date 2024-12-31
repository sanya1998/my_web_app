from app.common.schemas.user import (
    ManyUsersReadSchema,
    OneCreatedUserReadSchema,
    OneUserReadSchema,
    UserCreateSchema,
)
from app.common.tables import Users
from app.repositories.base import BaseRepository


class UserRepo(BaseRepository):
    db_model = Users

    one_read_schema = OneUserReadSchema
    many_read_schema = ManyUsersReadSchema
    one_created_read_schema = OneCreatedUserReadSchema
    create_schema = UserCreateSchema
