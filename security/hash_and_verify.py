"""Password hashing utilities used by the user and refresh-token store."""

from fastapi import HTTPException
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError


# Use pwdlib's recommended configuration so password hashes can evolve with
# current best practices without duplicating algorithm parameters here.
context = PasswordHash.recommended()


def hash_keyword(password: str) -> str:
    """Hash a plaintext secret before it is written to persistent storage."""

    return context.hash(password)


def verify_keyword(plain_password: str, hashed_password: str) -> bool:
    """Compare a plaintext password with a stored password hash."""

    try:
        return context.verify(plain_password, hashed_password)
    except UnknownHashError:
        # Log this if you want to investigate bad hashes.
        raise HTTPException(status_code=403, detail="Password is not hashed")


# Public alias used by the rest of the app; retained for readable imports.
verify_password = verify_keyword
