import asyncio
from typing import List

from app.common.constants.cache import CacheObjectEnum, CacheListingEnum
from app.common.dependencies.auth.moderator import CurrentModeratorUserDep
from app.common.dependencies.filters_input.hotels import HotelsFiltersDep
from app.common.dependencies.input.hotels import (
    HotelInputCreateDep,
    HotelInputUpdateDep,
)
from app.common.dependencies.repositories.hotel import HotelRepoDep
from app.common.dependencies.services.cache import CacheServiceDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.multiple_results import MultipleResultsApiError
from app.common.exceptions.api.not_found import NotFoundApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.multiple_results import MultipleResultsRepoError
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.schemas.hotel import (
    HotelCreateSchema,
    HotelDeleteSchema,
    HotelReadSchema,
    HotelUpdateSchema,
    ManyHotelsReadSchema,
    OneHotelReadSchema,
)
from fastapi import APIRouter
from fastapi_cache.decorator import cache

router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.post("/for_moderator")
async def create_hotel_for_moderator(
    hotel_input: HotelInputCreateDep,
    hotel_repo: HotelRepoDep,
    cache_service: CacheServiceDep,
    moderator: CurrentModeratorUserDep,
) -> HotelReadSchema:
    try:
        hotel_create = HotelCreateSchema.model_validate(hotel_input)
        new_hotel = await hotel_repo.create(hotel_create)
        # TODO: отправлять в консюмер команду на очистку кеша
        await cache_service.delete_objects_cache(objects_name=CacheListingEnum.HOTELS)
        return new_hotel
    except BaseRepoError:
        raise BaseApiError


@router.get("/")
@cache(namespace=CacheListingEnum.HOTELS)
async def get_hotels(raw_filters: HotelsFiltersDep, hotel_repo: HotelRepoDep) -> List[ManyHotelsReadSchema]:
    try:
        return await hotel_repo.get_objects(raw_filters=raw_filters)
    except BaseRepoError:
        raise BaseApiError


@router.get("/{object_id}")
@cache(namespace=CacheObjectEnum.HOTEL)
async def get_hotel(object_id: int, hotel_repo: HotelRepoDep) -> OneHotelReadSchema:
    try:
        return await hotel_repo.get_object_with_join(id=object_id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except MultipleResultsRepoError:
        raise MultipleResultsApiError
    except BaseRepoError:
        raise BaseApiError


@router.put("/{object_id}/for_moderator")
async def update_hotel_for_moderator(
    object_id: int,
    hotel_input: HotelInputUpdateDep,
    hotel_repo: HotelRepoDep,
    cache_service: CacheServiceDep,
    moderator: CurrentModeratorUserDep,
) -> HotelReadSchema:
    try:
        hotel_update = HotelUpdateSchema.model_validate(hotel_input)
        updated_hotel = await hotel_repo.update(hotel_update, id=object_id)
        # TODO: отправлять в консюмер команду на очистку кеша
        await cache_service.delete_object_cache(object_name=CacheObjectEnum.HOTEL, object_id=object_id)
        await cache_service.delete_objects_cache(objects_name=CacheListingEnum.HOTELS)
        return updated_hotel
    except NotFoundRepoError:
        raise NotFoundApiError
    except BaseRepoError:
        raise BaseApiError


@router.delete("/{object_id}/for_moderator")
async def delete_hotel_for_moderator(
    object_id: int, hotel_repo: HotelRepoDep, cache_service: CacheServiceDep, moderator: CurrentModeratorUserDep
) -> HotelDeleteSchema:
    try:
        deleted_hotel = await hotel_repo.delete_object(id=object_id)
        # TODO: отправлять в консюмер команду на очистку кеша
        await cache_service.delete_object_cache(object_name=CacheObjectEnum.HOTEL, object_id=object_id)
        await cache_service.delete_objects_cache(objects_name=CacheListingEnum.HOTELS)
        return deleted_hotel
    except NotFoundRepoError:
        raise NotFoundApiError
    except BaseRepoError:
        raise BaseApiError
