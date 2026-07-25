from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    school_id: UUID | None
    full_name: str
    role: str
    is_active: bool
