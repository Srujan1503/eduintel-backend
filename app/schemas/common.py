import math
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def build(cls, items: list[T], total: int, page: int, page_size: int) -> "PaginatedResponse[T]":
        total_pages = max(1, math.ceil(total / page_size)) if page_size else 1
        return cls(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
