from tests.common import TestClient


async def test_multy_clients(
    admin_client: TestClient,
    manager_client: TestClient,
    moderator_client: TestClient,
    user_client: TestClient,
    client: TestClient,
):
    """
    Проверка, что в одном тесте можно использовать сразу несколько клиентов с разными ролями
    """
    assert len({admin_client, manager_client, moderator_client, user_client, client}) == 5
