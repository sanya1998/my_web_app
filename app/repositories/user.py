from app.common.schemas.user import UserBaseReadSchema, UserCreateSchema
from app.common.tables import Users
from app.repositories.base import BaseRepository


class UserRepo(BaseRepository):
    db_model = Users

    one_read_schema = UserBaseReadSchema
    many_read_schema = UserBaseReadSchema
    one_created_read_schema = UserBaseReadSchema

    create_schema = UserCreateSchema
