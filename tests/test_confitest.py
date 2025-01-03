from httpx import AsyncClient


async def test_multy_clients(
    admin_client: AsyncClient,
    manager_client: AsyncClient,
    moderator_client: AsyncClient,
    user_client: AsyncClient,
    client: AsyncClient,
):
    """
    Проверка, что в одном тесте можно использовать сразу несколько клиентов с разными ролями
    """
    assert len({admin_client, manager_client, moderator_client, user_client, client}) == 5
