import pytest
from app.common.exceptions.repositories import NotFoundRepoError
from app.repositories import UserRepo


@pytest.mark.parametrize(
    "user_id, email, is_exist",
    [
        (1, "user@example.com", True),
        (100500, "...", False),
    ],
)
async def test_get_user_by_id(session, user_id, email, is_exist):
    try:
        user = await UserRepo(session).get_object(id=user_id)
        assert is_exist
        assert user.email == email
    except NotFoundRepoError:
        assert not is_exist
