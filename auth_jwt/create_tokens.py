from datetime import datetime, timedelta, timezone
import os
from uuid import uuid4

from bson import ObjectId
from dotenv import load_dotenv
from jose import JWTError, jwt
from pydantic import BaseModel


load_dotenv()

# Token settings are kept in environment variables so secrets and lifetimes can
# change per deployment without touching application code.
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set in .env")


class TokenUser(BaseModel):
    user_id: str
    session_id: str


def create_access_token(user: TokenUser) -> str:
    """Create a short-lived JWT used to authorize protected API requests."""

    payload = {
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "sub": user.user_id,
        "session_id": user.session_id,
        "type": "access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def refresh_token(user: TokenUser) -> str:
    """Create a long-lived JWT used only for issuing replacement token pairs."""

    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "sub": user.user_id,
        "session_id": user.session_id,
        "type": "refresh",
        # A unique ID gives each refresh token a different hash when persisted.
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict | None:
    """Decode a JWT and return its claims, or None when validation fails."""

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

    return payload
