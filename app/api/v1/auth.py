from fastapi import APIRouter, Depends

from app.auth.dependencies import CurrentUser, get_current_user
from app.schemas.auth import CurrentUserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=CurrentUserResponse)
def read_current_user(user: CurrentUser = Depends(get_current_user)) -> CurrentUserResponse:
    """Returns the identity FastAPI resolved from the caller's Supabase JWT.
    The frontend calls this right after login to hydrate its auth context."""
    return CurrentUserResponse(
        id=user.id,
        school_id=user.school_id,
        full_name=user.profile.full_name,
        role=user.role_name,
        is_active=user.profile.is_active,
    )
