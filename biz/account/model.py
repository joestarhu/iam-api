from sqlalchemy import String, SmallInteger, text
from sqlalchemy.orm import Mapped as M, mapped_column as mc

from core.orm import ModelBase, EMPTY_STR
from .schema import AccountFields, AccountStatusOpts


class Account(ModelBase):
    __tablename__ = "t_account"
    __table_args__ = (
        {"comment": "账号信息"}
    )

    account_uuid: M[str] = mc(
        type_=String(AccountFields.account_uuid.len),
        **AccountFields.account_uuid.orm_kwargs,
    )

    account: M[str] = mc(
        String(AccountFields.account.len),
        **AccountFields.account.orm_kwargs,
    )

    nickname: M[str] = mc(
        String(AccountFields.nickname.len),
        **AccountFields.nickname.orm_kwargs,
    )

    avatar_url: M[str] = mc(
        String(AccountFields.avatar_url.len),
        server_default=EMPTY_STR,
        **AccountFields.avatar_url.orm_kwargs
    )

    email: M[str] = mc(
        String(AccountFields.email.len),
        server_default=EMPTY_STR,
        **AccountFields.email.orm_kwargs
    )

    phone_enc: M[str] = mc(
        String(AccountFields.phone_enc.len),
        server_default=EMPTY_STR,
        **AccountFields.phone_enc.orm_kwargs
    )

    account_status: M[AccountStatusOpts] = mc(
        SmallInteger,
        server_default=text(f"{AccountStatusOpts.ENABLE.value}"),
        **AccountFields.account_status.orm_kwargs
    )

    password_hash: M[str] = mc(
        String(AccountFields.password_hash.len),
        server_default=EMPTY_STR,
        **AccountFields.password_hash.orm_kwargs
    )
