from datetime import date

from app.common.api_models.base import BaseModel


class SBooking(BaseModel):
    room_id: int
    date_from: date
    date_to: date
