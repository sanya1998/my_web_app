from app.cms.views.base import BaseView
from app.common.helpers.db import get_columns_by_table
from app.common.tables import Rooms


class RoomsView(BaseView, model=Rooms):
    name = "Номер"
    name_plural = "Номера"
    icon = "fa-solid fa-bed"

    column_list = [*get_columns_by_table(Rooms), Rooms.hotel]
