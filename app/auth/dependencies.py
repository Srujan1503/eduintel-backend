from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.jwt import TokenError, decode_supabase_jwt
from app.database.session import get_db
from app.models.profile import Profile
from app.models.role import Role

bearer_scheme = HTTPBearer(auto_error=False)


class CurrentUser:
    """Resolved identity for the authenticated request: Supabase auth.users id
    plus the tenant (school) and role looked up from the `profiles` table."""

    def __init__(self, profile: Profile, role_name: str):
        self.id: UUID = profile.id
        self.school_id: UUID | None = profile.school_id
        self.role_name = role_name
        self.profile = profile


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    try:
        payload = decode_supabase_jwt(credentials.credentials)
    except TokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    profile = db.get(Profile, UUID(payload["sub"]))
    if profile is None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="No profile found for this account yet",
        )
    if not profile.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="This account has been deactivated")

    role = db.get(Role, profile.role_id)
    return CurrentUser(profile=profile, role_name=role.name if role else "viewer")


def require_role(*allowed_roles: str):
    """Dependency factory: 403s unless the caller holds one of the given roles
    (super_admin always passes)."""

    def _dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role_name != "super_admin" and user.role_name not in allowed_roles:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return user

    return _dependency


def require_school(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Ensures the caller is linked to a school before touching tenant-scoped data."""
    if user.role_name != "super_admin" and user.school_id is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="This account is not linked to a school yet",
        )
    return user
