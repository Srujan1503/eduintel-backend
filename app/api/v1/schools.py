from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.school import SchoolCreate, SchoolUpdate, SchoolResponse
from app.schemas.common import PaginationParams, PaginatedResponse
from app.services.school_service import SchoolService
from app.auth.dependencies import require_role, require_school

router = APIRouter(prefix="/schools", tags=["schools"])


@router.post("/", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
def create_school(
    payload: SchoolCreate,
    db: Session = Depends(get_db),
    _ = Depends(require_role("super_admin")),
):
    service = SchoolService(db)
    school = service.create(payload)
    return school


@router.get("/", response_model=PaginatedResponse[SchoolResponse])
def list_schools(
    pagination: PaginationParams = Depends(),
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = SchoolService(db)
    items, total = service.search(q=q, page=pagination.page, page_size=pagination.page_size)
    return PaginatedResponse.build(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{school_id}", response_model=SchoolResponse)
def get_school(school_id: UUID, db: Session = Depends(get_db)):
    service = SchoolService(db)
    obj = service.get(school_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="School not found")
    return obj


@router.put("/{school_id}", response_model=SchoolResponse)
def update_school(
    school_id: UUID,
    payload: SchoolUpdate,
    db: Session = Depends(get_db),
    _ = Depends(require_role("super_admin")),
):
    service = SchoolService(db)
    obj = service.get(school_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="School not found")
    updated = service.update(obj, payload)
    return updated


@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_school(school_id: UUID, db: Session = Depends(get_db), _ = Depends(require_role("super_admin"))):
    service = SchoolService(db)
    obj = service.get(school_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="School not found")
    service.delete(obj)
    return None
