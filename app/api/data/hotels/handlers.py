from typing import Annotated, List

from app.common.constants.cache_prefixes import HOTELS_CACHE_PREFIX
from app.common.constants.paths import HOTELS_PATH, PATTERN_OBJECT_ID
from app.common.constants.tags import TagsEnum
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.helpers.response import BaseResponse
from app.common.schemas.hotel import HotelBaseReadSchema, HotelReadSchema, ManyHotelsReadSchema
from app.config.common import settings
from app.dependencies.auth.moderator import ModeratorUserAnn, ModeratorUserDep
from app.dependencies.filters import HotelsFiltersDep
from app.dependencies.input import HotelInputCreateDep, HotelInputUpdateDep
from app.dependencies.input.hotels import HotelInputPatchDep
from app.dependencies.repositories import HotelRepoDep
from app.exceptions.api import NotFoundApiError
from app.exceptions.repositories import NotFoundRepoError
from app.services import CacheService
from app.services.cache.key_builders.listing import build_key_by_listing, build_key_pattern_by_listing
from app.services.cache.key_builders.object_id import build_key_by_object_id
from fastapi import Path
from starlette import status

router = VersionedAPIRouter(prefix=HOTELS_PATH, tags=[TagsEnum.HOTELS])
cache = CacheService(
    prefix_key=HOTELS_CACHE_PREFIX,
    expire=settings.CACHE_EXPIRE_HOTELS,
    build_key_for_clear=build_key_by_object_id,  # TODO: pycharm подчеркивает
    build_key_pattern_for_clear=build_key_pattern_by_listing,
)


@router.post("/", response_model=BaseResponse[HotelBaseReadSchema], status_code=status.HTTP_201_CREATED)
async def create_hotel_for_moderator(
    hotel_input: HotelInputCreateDep,
    hotel_repo: HotelRepoDep,
    moderator: ModeratorUserAnn,
):
    new_hotel = await hotel_repo.create(hotel_input)
    # TODO: отправлять в консюмер команду на очистку кеша ?
    await cache.clear(clear_by_pattern=True)
    return BaseResponse(content=new_hotel)


@router.get("/", response_model=BaseResponse[List[ManyHotelsReadSchema]])
@cache.caching(build_key=build_key_by_listing)  # TODO: pycharm подчеркивает
async def get_hotels(filters: HotelsFiltersDep, hotel_repo: HotelRepoDep):
    hotels = await hotel_repo.get_objects(filters=filters)
    return BaseResponse(content=hotels)


@router.get(PATTERN_OBJECT_ID, response_model=BaseResponse[HotelReadSchema])
@cache.caching(build_key=build_key_by_object_id)  # TODO: pycharm подчеркивает
async def get_hotel(object_id: Annotated[int, Path(gt=0)], hotel_repo: HotelRepoDep):
    try:
        hotel = await hotel_repo.get_object(id=object_id)
        return BaseResponse(content=hotel)
    except NotFoundRepoError:
        raise NotFoundApiError(detail="Hotel was not found")  # TODO: дублирование


@router.patch(PATTERN_OBJECT_ID, response_model=BaseResponse[HotelBaseReadSchema])
async def update_hotel_fields_for_moderator(
    object_id: int,
    hotel_input: HotelInputPatchDep,
    hotel_repo: HotelRepoDep,
    moderator: ModeratorUserAnn,
):
    try:
        patched_hotel = await hotel_repo.update_object_fields(hotel_input, id=object_id)
        # TODO: отправлять в консюмер команду на очистку кеша ?
        await cache.clear(clear_by_key=True, clear_by_pattern=True, object_id=object_id)
        return BaseResponse(content=patched_hotel)
    except NotFoundRepoError:
        raise NotFoundApiError(detail="Hotel was not found")  # TODO: дублирование


@router.put(PATTERN_OBJECT_ID, response_model=BaseResponse[HotelBaseReadSchema], dependencies=[ModeratorUserDep])
async def update_hotel_for_moderator(
    object_id: int,
    hotel_input: HotelInputUpdateDep,
    hotel_repo: HotelRepoDep,
):
    try:
        updated_hotel = await hotel_repo.update(hotel_input, id=object_id)
        # TODO: отправлять в консюмер команду на очистку кеша ?
        await cache.clear(clear_by_key=True, clear_by_pattern=True, object_id=object_id)
        return BaseResponse(content=updated_hotel)
    except NotFoundRepoError:
        raise NotFoundApiError(detail="Hotel was not found")  # TODO: дублирование


@router.delete(PATTERN_OBJECT_ID, response_model=BaseResponse[HotelBaseReadSchema], dependencies=[ModeratorUserDep])
async def delete_hotel_for_moderator(object_id: int, hotel_repo: HotelRepoDep):
    try:
        deleted_hotel = await hotel_repo.delete_object(id=object_id)
        # TODO: отправлять в консюмер команду на очистку кеша ?
        await cache.clear(clear_by_key=True, clear_by_pattern=True, object_id=object_id)
        return BaseResponse(content=deleted_hotel)
    except NotFoundRepoError:
        raise NotFoundApiError(detail="Hotel was not found")  # TODO: дублирование
