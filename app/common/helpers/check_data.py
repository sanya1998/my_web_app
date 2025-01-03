from datetime import date
from typing import List

from pydantic import BaseModel


class CheckData(BaseModel):
    selected_room_id: int
    check_into: date
    check_out: date
    exclude_booking_ids: List[int] = list()
