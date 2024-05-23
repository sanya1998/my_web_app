import hashlib

from app.config.main import settings


class PasswordService:
    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return hashlib.sha256(password.encode(settings.ENCODING)).hexdigest()

    @classmethod
    def verify_password(cls, raw_password: str, hashed_password: str) -> bool:
        return cls.get_password_hash(raw_password) == hashed_password
