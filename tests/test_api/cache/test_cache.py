from typing import List

from app.common.constants.cache_prefixes import HOTELS_CACHE_PREFIX
from app.common.schemas.hotel import ManyHotelsReadSchema
from app.services import CacheService
from app.services.cache.key_builders.listing import build_key_pattern_by_listing
from tests.constants.urls import HOTELS_URL


async def take_endpoint(client):
    hotels = await client.get(HOTELS_URL, model=List[ManyHotelsReadSchema])
    return hotels


async def clear_cache():
    cache = CacheService(prefix_key=HOTELS_CACHE_PREFIX, build_key_pattern_for_clear=build_key_pattern_by_listing)
    await cache.clear(clear_by_pattern=True)


async def fake_response(self, filters):
    """
    Mock response HotelRepo.get_objects
    """
    return []


async def test_cache(client, mocker):
    await clear_cache()
    # Получение результата и его запись в кеш
    hotels = await take_endpoint(client)

    # Патч репозитория, чтобы теперь он возвращал фейковый ответ (не тот, что в бд)
    mocker.patch("app.repositories.hotel.HotelRepo.get_objects", fake_response)

    hotels_from_cache = await take_endpoint(client)
    # Несмотря на mock, endpoint вернул то, что в кеше, а не то что сейчас приходит из репозитория
    assert hotels == hotels_from_cache

    await clear_cache()
    hotels_mocked = await take_endpoint(client)
    # Кеша больше нет, поэтому теперь endpoint вернул то, то сейчас приходит из репозитория (mock)
    assert hotels_mocked != hotels_from_cache

    await clear_cache()


# TODO: тест кеша для одного отеля
