from typing import Any

from app.common.tables import Hotels, Rooms
from sqlalchemy import Select, func

from sqlalchemy_filterset import BaseFilter, Filter


def join_hotels_rooms(query: Select, values: dict):
    if values.get("join_rooms"):
        query = query.outerjoin(Rooms, Rooms.hotel_id == Hotels.id).distinct()
        values["join_rooms"] = False
    return query


class JoinHotelsRoomsFilter(BaseFilter):
    """
    Нужен, чтобы получить отели, у которых есть свободные номера на выбранные даты и/или в нужном диапазоне цен
    """

    def filter(self, query: Select, value: Any, values: dict):
        if not value:
            return query
        return join_hotels_rooms(query, values)
