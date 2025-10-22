import pytest
from app.dependencies.input.rooms import RoomUpsertInput
from app.exceptions.repositories.programming import ProgrammingRepoError
from app.repositories import RoomRepo


async def test_bad_upsert(postgres_session):
    with pytest.raises(ProgrammingRepoError):
        await RoomRepo(postgres_session).upsert(
            data=RoomUpsertInput(
                hotel_id=5,
                name="new room",
                price=5000,
                quantity=1,
            ),
            index_elements=[RoomRepo.db_model.name],
        )
