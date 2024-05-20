from app.common.schemas.base import BaseSchema


class HotelSchema(BaseSchema):
    hotel_id: int
    name: str
