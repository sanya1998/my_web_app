import copy
import hashlib
from datetime import datetime, timedelta

import jwt
from app.config.main import settings


class AuthorizationService:
    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return hashlib.sha256(password.encode(settings.ENCODING)).hexdigest()

    @classmethod
    def verify(cls, hashed_password_1, hashed_password_2) -> bool:
        return hashed_password_1 == hashed_password_2

    @classmethod
    def create_access_token(cls, data: dict) -> str:
        to_encode = copy.deepcopy(data)
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(payload=to_encode, key=settings.JWT_SECRET_KEY)
        return encoded_jwt
