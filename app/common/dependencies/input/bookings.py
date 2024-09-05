from typing import Annotated

from app.common.schemas.booking import BookingInputSchema
from fastapi import Depends

BookingInputDep = Annotated[BookingInputSchema, Depends(BookingInputSchema)]
