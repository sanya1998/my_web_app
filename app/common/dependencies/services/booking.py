from typing import Annotated

from app.common.dependencies.repositories.booking import BookingRepoDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.services.base import BaseServiceError
from app.services.booking import BookingService
from fastapi import Depends


def get_booking_service(booking_repo: BookingRepoDep):
    try:
        return BookingService(booking_repo=booking_repo)
    except BaseServiceError:
        raise BaseApiError


BookingServiceDep = Annotated[BookingService, Depends(get_booking_service)]
