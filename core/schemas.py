from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar, Annotated

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar("T")

# Global UUID length
UUID_LENGTH: int = 48

# Default page constant
DEFAULT_PAGE_NUM: int = 1
DEFAULT_PAGE_SIZE: int = 10


@dataclass(slots=True, frozen=True)
class APIPermission:
    path: str
    summary: str
    scope: str

    @property
    def method_kwargs(self) -> dict:
        return {
            "path": self.path,
            "summary": self.summary
        }


@dataclass(slots=True, frozen=True)
class Actor:
    session: AsyncSession
    account_uuid: str
    scope: list[str] | None


@dataclass(slots=True, frozen=True)
class MF(Generic[T]):
    comment: str
    len: int | None = None
    min_value: int | float | None = None
    max_value: int | float | None = None
    pattern: str | None = None
    unique: bool = False
    default_value: T | None = None

    @property
    def orm_kwargs(self) -> dict:
        """For ORM Model Arguments"""
        args = {
            "unique": self.unique,
            "comment": self.comment,
        }

        return args

    @property
    def field_kwargs(self) -> dict:
        """Pydantic Field"""
        args = {
            "description": self.comment,
        }

        args |= {
            key: value for key, value in [
                ("pattern", self.pattern),
                ("max_length", self.len),
                ("min_value", self.min_value),
                ("max_value", self.max_value),
            ] if value is not None
        }

        return args


class APIResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "Succeed"
    data: T


class Pagination(BaseModel):
    page_num: int = Field(default=DEFAULT_PAGE_NUM, description="当前页码")
    page_size: int = Field(default=DEFAULT_PAGE_SIZE, description="每页数量")


class PaginationData(Pagination, Generic[T]):
    total_items: int = Field(default=0, description="数据总数")
    total_pages: int = Field(default=1, description="总页数")
    items: list[T] = Field(default_factory=list, description="数据")
