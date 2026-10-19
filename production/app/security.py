import hashlib
import secrets
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    try:
        return _hasher.verify(encoded, password)
    except VerifyMismatchError:
        return False


def issue_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    return token, hashlib.sha256(token.encode()).hexdigest()
