from typing import List

from app.common.dependencies.auth.moderator import CurrentModeratorUserDep
from app.common.dependencies.filters_input.hotels import HotelsFiltersDep
from app.common.dependencies.input.hotels import (
    HotelInputCreateDep,
    HotelInputUpdateDep,
)
from app.common.dependencies.repositories.hotel import HotelRepoDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.multiple_results import MultipleResultsApiError
from app.common.exceptions.api.not_found import NotFoundApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.multiple_results import MultipleResultsRepoError
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.schemas.hotel import (
    HotelCreateSchema,
    HotelUpdateSchema,
    ManyHotelsReadSchema,
    OneHotelReadSchema,
)
from fastapi import APIRouter

router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.post("/for_moderator")
async def create_hotel_for_moderator(
    hotel_input: HotelInputCreateDep, hotel_repo: HotelRepoDep, moderator: CurrentModeratorUserDep
) -> OneHotelReadSchema:
    try:
        hotel_create = HotelCreateSchema.model_validate(hotel_input)
        return await hotel_repo.create(hotel_create)
    except BaseRepoError:
        raise BaseApiError


@router.get("/")
async def get_hotels(raw_filters: HotelsFiltersDep, hotel_repo: HotelRepoDep) -> List[ManyHotelsReadSchema]:
    try:
        return await hotel_repo.get_objects(raw_filters=raw_filters)
    except BaseRepoError:
        raise BaseApiError


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int, hotel_repo: HotelRepoDep) -> OneHotelReadSchema:
    try:
        return await hotel_repo.get_object(id=hotel_id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except MultipleResultsRepoError:
        raise MultipleResultsApiError
    except BaseRepoError:
        raise BaseApiError


@router.put("/{hotel_id}/for_moderator")
async def update_hotel_for_moderator(
    hotel_id: int, hotel_input: HotelInputUpdateDep, hotel_repo: HotelRepoDep, moderator: CurrentModeratorUserDep
) -> OneHotelReadSchema:
    try:
        hotel_update = HotelUpdateSchema.model_validate(hotel_input)
        return await hotel_repo.update(hotel_update, id=hotel_id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except BaseRepoError:
        raise BaseApiError


@router.delete("/{hotel_id}/for_moderator")
async def delete_hotel_for_moderator(
    hotel_id: int, hotel_repo: HotelRepoDep, moderator: CurrentModeratorUserDep
) -> OneHotelReadSchema:
    try:
        return await hotel_repo.delete_object(id=hotel_id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except BaseRepoError:
        raise BaseApiError
