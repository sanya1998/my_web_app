import copy
from datetime import datetime, timedelta
from typing import List

import jwt
from app.config.common import settings
from app.exceptions.services import (
    ExpiredSignatureServiceError,
    InvalidAlgorithmServiceError,
    InvalidTokenServiceError,
    MissingRequiredClaimServiceError,
)
from app.repositories import UserRepo
from app.services import BaseService
from jwt.exceptions import ExpiredSignatureError, InvalidAlgorithmError, InvalidTokenError, MissingRequiredClaimError


class BaseAuthService(BaseService):
    @BaseService.catcher
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    @classmethod
    @BaseService.catcher
    def create_access_token(
        cls,
        data: dict,
        key: str = settings.JWT_SECRET_KEY,
        algorithm: List[str] = settings.ENCODE_ALGORITHM,
        expires_delta: timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    ) -> str:
        to_encode = copy.deepcopy(data)
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(payload=to_encode, key=key, algorithm=algorithm)
        return encoded_jwt

    @classmethod
    @BaseService.catcher
    def decrypt_access_token(
        cls, token: str, key: str = settings.JWT_SECRET_KEY, algorithms: List[str] = settings.DECODE_ALGORITHMS
    ) -> dict:
        try:
            payload = jwt.decode(jwt=token, key=key, algorithms=algorithms, options={"require": ["exp", "sub"]})
            return payload  # TODO: pydantic model
        except MissingRequiredClaimError:
            raise MissingRequiredClaimServiceError
        except ExpiredSignatureError:
            raise ExpiredSignatureServiceError
        except InvalidAlgorithmError:
            raise InvalidAlgorithmServiceError
        except InvalidTokenError:
            raise InvalidTokenServiceError
