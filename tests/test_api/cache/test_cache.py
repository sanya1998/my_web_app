from app.common.constants.cache_prefixes import HOTELS_CACHE_PREFIX
from app.services.cache.cache import CacheService
from app.services.cache.key_builders.listing import build_key_pattern_by_listing
from tests.constants import BASE_HOTELS_URL


async def take_endpoint(client):
    response = await client.get(BASE_HOTELS_URL)
    return response.json()


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
    first_response = await take_endpoint(client)

    mocker.patch("app.repositories.hotel.HotelRepo.get_objects", fake_response)

    response_from_cache = await take_endpoint(client)
    # Несмотря на mock, ответы равны, благодаря кешу
    assert first_response == response_from_cache

    await clear_cache()
    mocked_response = await take_endpoint(client)
    # Кеша больше нет, поэтому теперь будет фейковый ответ, который отличается от реального
    assert first_response != mocked_response

    await clear_cache()


# TODO: тест кеша для одного отеля
