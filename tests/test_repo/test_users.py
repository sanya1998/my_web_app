import pytest
from app.common.schemas.user import UserCreateSchema
from app.exceptions.repositories import NotFoundRepoError
from app.exceptions.repositories.integrity import IntegrityRepoError
from app.repositories import UserRepo
from tests.constants.users_info import USER_EMAIL


@pytest.mark.parametrize(
    "user_id, email, is_exist",
    [
        (1, "user@example.com", True),
        (100500, "...", False),
    ],
)
async def test_get_user_by_id(postgres_session, user_id, email, is_exist):
    try:
        user = await UserRepo(postgres_session).get_object(id=user_id)
        assert is_exist
        assert user.email == email
    except NotFoundRepoError:
        assert not is_exist


async def test_unique_email(postgres_session):
    with pytest.raises(IntegrityRepoError):
        await UserRepo(postgres_session).create(
            UserCreateSchema(email=USER_EMAIL, hashed_password="hashed_password", roles=["user"])
        )
