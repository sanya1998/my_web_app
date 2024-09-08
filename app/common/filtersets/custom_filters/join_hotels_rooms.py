from typing import Any

from app.common.tables import Hotels, Rooms
from sqlalchemy import Select
from sqlalchemy_filterset import BaseFilter


class JoinHotelsRoomsFilter(BaseFilter):
    """
    Нужен, чтобы получить отели, у которых есть свободные номера на выбранные даты и/или в нужном диапазоне цен
    """

    def filter(self, query: Select, value: Any, values: dict):
        if not value:
            return query
        return query.outerjoin(Rooms, Rooms.hotel_id == Hotels.id).distinct()
