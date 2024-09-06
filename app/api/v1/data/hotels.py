from typing import List

from app.common.dependencies.filters.hotels import HotelsFiltersDep
from app.common.dependencies.repositories.hotel import HotelRepoDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.multiple_results import MultipleResultsApiError
from app.common.exceptions.api.not_found import NotFoundApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.multiple_results import MultipleResultsRepoError
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.schemas.hotel import HotelReadSchema
from fastapi import APIRouter

router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int, hotel_repo: HotelRepoDep) -> HotelReadSchema:
    try:
        return await hotel_repo.get_object(id=hotel_id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except MultipleResultsRepoError:
        raise MultipleResultsApiError
    except BaseRepoError:
        raise BaseApiError


@router.get("/")
async def get_hotels(raw_filters: HotelsFiltersDep, hotel_repo: HotelRepoDep) -> List[HotelReadSchema]:
    try:
        return await hotel_repo.get_objects(raw_filters=raw_filters)
    except BaseRepoError:
        raise BaseApiError
