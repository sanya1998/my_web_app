from datetime import date
from typing import List

from pydantic import BaseModel


class CheckData(BaseModel):
    check_into: date | None = None
    check_out: date | None = None
    exclude_booking_ids: List[int] = list()
