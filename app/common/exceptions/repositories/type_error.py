from app.common.exceptions.repositories.base import BaseRepoError


class RepoTypeError(BaseRepoError):
    problem: str = "Type error"
