from pydantic import BaseModel, Field

from biz.account.schema import AccountFields


class ReqPasswordLogin(BaseModel):
    """账密登录请求"""
    account: str = Field(description=AccountFields.account.comment)
    password: str = Field(description=AccountFields.password_hash.comment)


class RespJWT(BaseModel):
    """JWT"""
    access_token: str = Field(description="AccessToken")


class RespProfile(BaseModel):
    account: str = Field(description=AccountFields.account.comment)
    nickname: str = Field(description=AccountFields.nickname.comment)
    avatar_url: str = Field(description=AccountFields.avatar_url.comment)
    phone_masked: str = Field(description=AccountFields.phone_masked.comment)
    email: str = Field(description=AccountFields.email.comment)
