from app.common.exceptions.repositories.base import BaseRepoError


class RepoNotFoundError(BaseRepoError):
    problem: str = "Not found"
