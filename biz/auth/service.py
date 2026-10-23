
from sqlalchemy import select

from core.schemas import Actor
from core.errors import APIError, BizError
from core.orm import ORM, AsyncSession
from core.utils import SecurityUtils, jwt_manager

from biz.account.model import Account as ta, AccountStatusOpts
from biz.auth.schema import RespJWT, RespProfile


def generate_jwt(account_uuid: str, account_status: int) -> RespJWT:
    if account_status == AccountStatusOpts.DISABLE.value:
        raise BizError(APIError.AUTH_ERR_ACCOUNT_DISABLED)

    token = jwt_manager.encode(account_uuid=account_uuid)
    return RespJWT(access_token=token)


class AuthService:
    @staticmethod
    async def password_login(
        account: str,
        password: str,
        session: AsyncSession
    ) -> RespJWT:
        stmt = select(
            ta.account_uuid,
            ta.account,
            ta.account_status,
            ta.password_hash
        ).where(
            ta.account == account
        ).limit(1)
        row = await ORM.first(session, stmt)
        # 账号不存在或密码为空
        if row is None or len(row.password_hash) == 0:
            raise BizError(APIError.AUTH_ERR_PASSWORD_LOGIN)

        # 密码不匹配
        if not SecurityUtils.password_verify(password, row.password_hash):
            raise BizError(APIError.AUTH_ERR_PASSWORD_LOGIN)

        return generate_jwt(row.account_uuid, row.account_status)

    @staticmethod
    async def get_profile(
        actor: Actor
    ) -> RespProfile:
        stmt = select(
            ta.account,
            ta.nickname,
            ta.avatar_url,
            ta.phone_enc,
            ta.email
        ).where(
            ta.account_uuid == actor.account_uuid
        ).limit(1)
        item = await ORM.first(actor.session, stmt)

        if item:
            phone_masked = SecurityUtils.phone_decrypt(item.phone_enc)
            data = RespProfile(**item, phone_masked=phone_masked)
        else:
            raise BizError(APIError.ACCOUNT_ERR_NOT_FOUND)

        return data
