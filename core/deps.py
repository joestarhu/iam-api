from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Query
from fastapi.security import SecurityScopes, OAuth2PasswordBearer
from jose.exceptions import ExpiredSignatureError

from core.orm import LocalSession
from core.schemas import Actor, DEFAULT_PAGE_NUM, DEFAULT_PAGE_SIZE, Pagination
from core.utils import jwt_manager

oauth2 = OAuth2PasswordBearer("/auth/docs-login")


async def get_sesion() -> AsyncGenerator:
    """获取数据库异步会话"""
    async with LocalSession() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise


async def get_actor(
    scopes: SecurityScopes,
    session=Depends(get_sesion),
    token=Depends(oauth2),
) -> Actor:
    """获取操作用户信息"""
    try:
        payload = jwt_manager.decode(token)
    except ExpiredSignatureError as e:
        raise HTTPException(401, detail=f"{e}")
    except Exception as e:
        raise HTTPException(500, detail=f"{e}")

    account_uuid = payload.get("account_uuid", "")
    if not account_uuid:
        raise HTTPException(401, detail="无法从jwt中获取到account_uuid")

    if scopes.scopes:

        # 调用服务需要权限标识
        raise HTTPException(403, detail="无权限访问")

    return Actor(session, account_uuid, None)


async def get_pagination(
    page_num: int = Query(default=DEFAULT_PAGE_NUM, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=100),
) -> Pagination:
    """获取分页信息"""
    return Pagination(page_num=page_num, page_size=page_size)
