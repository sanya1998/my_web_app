from typing import List

from app.common.constants.cache_prefixes import HOTELS_CACHE_PREFIX
from app.common.dependencies.auth.moderator import ModeratorUserDep
from app.common.dependencies.filters.hotels import HotelsFiltersDep
from app.common.dependencies.input.hotels import HotelBaseInput, HotelInputCreateDep, HotelInputUpdateDep
from app.common.dependencies.repositories.hotel import HotelRepoDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.multiple_results import MultipleResultsApiError
from app.common.exceptions.api.not_found import NotFoundApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.multiple_results import MultipleResultsRepoError
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.schemas.hotel import HotelBaseReadSchema, HotelReadSchema, ManyHotelsReadSchema
from app.config.common import settings
from app.services.cache.cache import CacheService
from app.services.cache.key_builders.listing import build_key_by_listing, build_key_pattern_by_listing
from app.services.cache.key_builders.object_id import build_key_by_object_id

router = VersionedAPIRouter(prefix="/hotels", tags=["Hotels"])
cache = CacheService(
    prefix_key=HOTELS_CACHE_PREFIX,
    expire=settings.CACHE_EXPIRE_HOTELS,
    build_key_for_clear=build_key_by_object_id,  # TODO: pycharm подчеркивает
    build_key_pattern_for_clear=build_key_pattern_by_listing,
)


@router.post("/for_moderator")
async def create_hotel_for_moderator(
    hotel_input: HotelInputCreateDep,
    hotel_repo: HotelRepoDep,
    moderator: ModeratorUserDep,
) -> HotelBaseReadSchema:
    try:
        hotel_create = HotelBaseInput.model_validate(hotel_input)
        new_hotel = await hotel_repo.create(hotel_create)
        # TODO: отправлять в консюмер команду на очистку кеша ?
        await cache.clear(clear_by_pattern=True)
        return new_hotel
    except BaseRepoError:
        raise BaseApiError


@router.get("/")
@cache.caching(build_key=build_key_by_listing)
async def get_hotels(filters: HotelsFiltersDep, hotel_repo: HotelRepoDep) -> List[ManyHotelsReadSchema]:
    try:
        return await hotel_repo.get_objects(filters=filters)
    except BaseRepoError:
        raise BaseApiError


@router.get("/{object_id}")
@cache.caching(build_key=build_key_by_object_id)  # TODO: pycharm подчеркивает
async def get_hotel(object_id: int, hotel_repo: HotelRepoDep) -> HotelReadSchema:
    try:
        return await hotel_repo.get_object(id=object_id)
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
    moderator: ModeratorUserDep,
) -> HotelBaseReadSchema:
    try:
        hotel_update = HotelBaseInput.model_validate(hotel_input)
        updated_hotel = await hotel_repo.update(hotel_update, id=object_id)
        # TODO: отправлять в консюмер команду на очистку кеша ?
        await cache.clear(clear_by_key=True, clear_by_pattern=True, object_id=object_id)
        return updated_hotel
    except NotFoundRepoError:
        raise NotFoundApiError
    except BaseRepoError:
        raise BaseApiError


@router.delete("/{object_id}/for_moderator")
async def delete_hotel_for_moderator(
    object_id: int, hotel_repo: HotelRepoDep, moderator: ModeratorUserDep
) -> HotelBaseReadSchema:
    try:
        deleted_hotel = await hotel_repo.delete_object(id=object_id)
        # TODO: отправлять в консюмер команду на очистку кеша ?
        await cache.clear(clear_by_key=True, clear_by_pattern=True, object_id=object_id)
        return deleted_hotel
    except NotFoundRepoError:
        raise NotFoundApiError
    except BaseRepoError:
        raise BaseApiError
