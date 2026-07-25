"""Verification of Supabase Auth JWTs.

Supabase issues access tokens signed (HS256) with the project's JWT secret
(Project Settings > API > JWT Secret). FastAPI never issues its own session
tokens -- it only verifies the ones Supabase already issued.
"""

import jwt
from jwt import PyJWTError

from app.core.config import get_settings

ALGORITHM = "HS256"
AUDIENCE = "authenticated"


class TokenError(Exception):
    """Raised when a bearer token fails verification."""


def decode_supabase_jwt(token: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=[ALGORITHM],
            audience=AUDIENCE,
        )
    except PyJWTError as exc:
        raise TokenError(str(exc)) from exc

    if not payload.get("sub"):
        raise TokenError("Token is missing a subject claim")

    return payload
