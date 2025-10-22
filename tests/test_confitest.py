from tests.common import CustomAsyncClient


async def test_multy_clients(
    admin_client: CustomAsyncClient,
    manager_client: CustomAsyncClient,
    moderator_client: CustomAsyncClient,
    user_client: CustomAsyncClient,
    client: CustomAsyncClient,
):
    """
    Проверка, что в одном тесте можно использовать сразу несколько клиентов с разными ролями
    """
    assert len({admin_client, manager_client, moderator_client, user_client, client}) == 5
