from app.cms.views.base import BaseView
from app.common.helpers.db import get_columns_by_table
from app.common.tables import Hotels


class HotelsView(BaseView, model=Hotels):
    name = "Отель"
    name_plural = "Отели"
    icon = "fa-solid fa-hotel"

    column_list = get_columns_by_table(Hotels)
