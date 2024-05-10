from datetime import date
from typing import Annotated, Optional

from fastapi import Depends, Query


class HotelsFilters:
    def __init__(
        self,
        location: str,
        date_from: date,
        date_to: date,
        has_spa: Optional[bool] = None,
        stars: Optional[int] = Query(default=None, ge=1, le=5),
    ):
        self.location = location
        self.date_from = date_from
        self.date_to = date_to
        self.has_spa = has_spa
        self.stars = stars


HotelsFiltersDep = Annotated[HotelsFilters, Depends(HotelsFilters)]
