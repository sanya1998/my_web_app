from app.common.schemas.user import UserCreateSchema, UserReadSchema
from app.common.tables import Users
from app.repositories.base import BaseRepository


class UserRepo(BaseRepository):
    db_model = Users

    read_schema = UserReadSchema
    create_schema = UserCreateSchema
