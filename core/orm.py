from math import ceil
from typing import Annotated, Type

from fastapi import HTTPException

from sqlalchemy import text, String, event, Select, select, func
from sqlalchemy.orm import Mapped as M, mapped_column as mc, DeclarativeBase, ORMExecuteState, with_loader_criteria, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from rgt.data import BaseMixin, SoftDeleteMixin

from core.schemas import UUID_LENGTH, Pagination, PaginationData, T
from core.config import settings

# 数据库异步引擎
engine = create_async_engine(**settings.orm_kwargs)

# 数据库异步会话
LocalSession: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False
)

# 数据类型
EMPTY_STR = text("''")

# 操作者UUID
ACTOR_UUID = Annotated[
    str,
    mc(String(UUID_LENGTH), server_default=EMPTY_STR)
]


class ModelBase(DeclarativeBase, BaseMixin, SoftDeleteMixin):
    created_by: M[ACTOR_UUID] = mc(comment="数据创建者UUID")
    updated_by: M[ACTOR_UUID] = mc(comment="数据更新者UUID")


# 全局注册软删除(※SQLALCHEMY的异步也是由同步的Session来实现)
@event.listens_for(Session, "do_orm_execute")
def add_soft_del_filter(state: ORMExecuteState) -> None:
    if (
        state.is_select
        and not state.is_column_load
        and not state.is_relationship_load
        and not state.execution_options.get("include_deleted", False)
    ):
        state.statement = state.statement.options(
            with_loader_criteria(
                SoftDeleteMixin,
                lambda cls: cls.is_deleted.is_(False),
                include_aliases=True
            )
        )


class ORM:
    @staticmethod
    async def first(session: AsyncSession, stmt: Select):
        try:
            rows = await session.execute(stmt)
            return rows.mappings().first()
        except Exception as e:
            raise HTTPException(500, detail=f"{e}")

    @staticmethod
    async def all(session: AsyncSession, stmt: Select, schema: Type[T] = dict) -> list[T]:
        try:
            rows = await session.execute(stmt)
            return [schema(**row) for row in rows.mappings()]
        except Exception as e:
            raise HTTPException(500, detail=f"{e}")

    @staticmethod
    async def counts(session: AsyncSession, stmt: Select) -> int:
        count_stmt = select(func.count()).select_from(
            stmt.order_by(None).subquery()
        )

        return await session.scalar(count_stmt) or 0

    @staticmethod
    async def pagination(
        session: AsyncSession,
        stmt: Select,
        pagination: Pagination,
        order_by_args: list | None = None,
        schema: Type[T] = dict
    ) -> PaginationData[T]:
        data = PaginationData(**pagination.model_dump())

        # 获取数据总数和页面总数
        data.total_items = await ORM.counts(session, stmt)

        data.total_pages = max(1, ceil(data.total_items / data.page_size))
        data.page_num = max(1, min(data.total_pages, data.page_num))

        # 没有数据
        if data.total_items == 0:
            return data

        # 排序
        page_stmt = stmt.order_by(*order_by_args) if order_by_args else stmt

        offset = (data.page_num-1) * data.page_size
        page_stmt = page_stmt.offset(offset).limit(data.page_size)

        data.items = await ORM.all(session, page_stmt, schema)

        return data
