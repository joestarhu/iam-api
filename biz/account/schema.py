from datetime import datetime
from enum import IntEnum
from pydantic import BaseModel, Field

from core.schemas import UUID_LENGTH, MF


class AccountStatusOpts(IntEnum):
    """账号状态"""
    ENABLE = 0
    DISABLE = 1


#  字段
class AccountFields:
    account_uuid = MF(
        comment="账号UUID",
        len=UUID_LENGTH,
        pattern=None,
        unique=True,
    )

    account = MF(
        comment="账号",
        len=32,
        pattern=r"^[a-z0-9_]{3,32}$",
        unique=True,
    )

    nickname = MF(
        comment="昵称",
        len=64,
        pattern=None
    )

    avatar_url = MF(
        comment="头像URL",
        len=2048,
        pattern=None
    )

    email = MF(
        comment="邮箱",
        len=254,
        pattern=r'^$|^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    phone_enc = MF(
        comment="手机号(加密存储)",
        len=320,
        pattern=None,
    )

    account_status = MF(
        comment="用户状态",
    )

    password_hash = MF(
        comment="账号密码(加密)",
        len=256,
    )

    phone = MF(
        comment="手机号(明文)",
        pattern=r"^(?:1[3-9]\d{9})?$"
    )

    phone_masked = MF(
        comment="手机号(脱敏),如151****1234",
    )

    password = MF(
        comment="密码(明文)",
        len=24,
    )


# 请求
class ReqCreateAccount(BaseModel):
    account: str = Field(**AccountFields.account.field_kwargs)
    nickname: str = Field(**AccountFields.nickname.field_kwargs)
    avatar_url: str = Field(
        default="", **AccountFields.avatar_url.field_kwargs)
    email: str = Field(default="", **AccountFields.email.field_kwargs)
    phone: str = Field(default="", **AccountFields.phone.field_kwargs)
    password_hash: str = Field(**AccountFields.password_hash.field_kwargs)


# 入参
class ParamsCreateAccount(BaseModel):
    account: str = Field(**AccountFields.account.field_kwargs)
    nickname: str = Field(**AccountFields.nickname.field_kwargs)
    avatar_url: str = Field(**AccountFields.avatar_url.field_kwargs)
    email: str = Field(**AccountFields.email.field_kwargs)
    phone: str = Field(**AccountFields.phone.field_kwargs)
    password: str = Field(**AccountFields.password.field_kwargs)
    account_status: AccountStatusOpts = Field(
        default=AccountStatusOpts.ENABLE, ** AccountFields.account_status.field_kwargs)


# 响应值
class RespCreateAccount(BaseModel):
    """创建用户的返回数据"""
    account_uuid: str


class AccountListResponse(BaseModel):
    """获取账号列表的返回数据"""
    account_uuid: str = Field(description=AccountFields.account_uuid.comment)
    account: str = Field(description=AccountFields.account.comment)
    nickname: str = Field(description=AccountFields.nickname.comment)
    avatar_url: str = Field(description=AccountFields.avatar_url.comment)
    account_status: AccountStatusOpts = Field(
        description=AccountFields.account_status.comment)
    phone_masked: str = Field(description=AccountFields.phone_masked.comment)
    email: str = Field(description=AccountFields.email.comment)
    created_at: datetime
