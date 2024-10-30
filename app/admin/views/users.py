from app.admin.views.base import BaseView
from app.common.tables import Users


class UsersView(BaseView, model=Users):
    name = "Пользователь"
    name_plural = "Пользователи"

    column_list = [Users.id, Users.email, Users.first_name, Users.last_name]

    column_details_exclude_list = [Users.hashed_password]

    can_delete = False
