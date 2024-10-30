from app.admin.views.base import BaseView
from app.common.helpers.db import get_columns_by_table
from app.common.tables import Bookings


class BookingsView(BaseView, model=Bookings):
    name = "Бронирование"
    name_plural = "Бронирования"
    icon = "fa-solid fa-book"

    column_list = [*get_columns_by_table(Bookings), Bookings.user]
