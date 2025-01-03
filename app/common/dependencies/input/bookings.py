from typing import Annotated

from app.common.schemas.booking import BookingCreateInputSchema, BookingUpdateInputSchema
from fastapi import Depends

BookingInputCreateDep = Annotated[BookingCreateInputSchema, Depends(BookingCreateInputSchema)]
BookingInputUpdateDep = Annotated[BookingUpdateInputSchema, Depends(BookingUpdateInputSchema)]
