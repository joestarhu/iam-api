
from sqlalchemy import or_, select

from core.orm import ORM, AsyncSession
from core.schemas import Actor, Pagination, PaginationData
from core.errors import APIError, BizError
from core.utils import normalize_str, UUIDGenUtils, SecurityUtils

from biz.account.model import Account as ta
from biz.account.schema import AccountStatusOpts, ParamsCreateAccount, RespCreateAccount


async def ensure_account_unique(
    session: AsyncSession,
    account_uuid: str | None = None,
    account: str | None = None,
    phone_enc: str | None = None,
    email: str | None = None,
    is_exlucde_uuid: bool = False,
) -> None:
    """账号唯一性检测"""
    account_uuid, account, phone_enc, email = map(
        normalize_str,
        [account_uuid, account, phone_enc, email]
    )

    # 构建查询条件
    or_conditions_args = [
        condition for flag, condition in [
            (account, ta.account == account),
            (phone_enc, ta.phone_enc == phone_enc),
            (email, ta.email == email),
            (is_exlucde_uuid == False, ta.account_uuid == account_uuid)
        ] if flag
    ]

    if len(or_conditions_args) == 0:
        return

    whereclause_args = []
    if is_exlucde_uuid:
        whereclause_args.append(ta.account_uuid != account_uuid)
    whereclause_args.append(or_(*or_conditions_args))

    stmt = select(
        ta.account_uuid,
        ta.account,
        ta.phone_enc,
        ta.email
    ).where(
        *whereclause_args
    )

    rows = await session.execute(stmt)

    check_fileds = [
        ("account_uuid", account_uuid),
        ("account", account),
        ("phone_enc", phone_enc),
        ("email", email),
    ]

    existed_fileds = []
    for row in rows.mappings():
        for field, value in check_fileds:
            target = row.get(field, None)
            if target and target == value:
                existed_fileds.append(field)

    if existed_fileds:
        raise BizError(APIError.ACCOUNT_ERR_UNIQUE, data=existed_fileds)


class AccountService:
    @staticmethod
    async def create_account(
        params: ParamsCreateAccount,
        actor: Actor,
    ) -> RespCreateAccount:
        session = actor.session
        account_uuid = UUIDGenUtils.account()
        account = params.account
        email = params.email
        phone_enc = SecurityUtils.phone_encrypt(params.phone)
        password = params.password

        password_hash = SecurityUtils.password_hash(password)

        await ensure_account_unique(
            session,
            account_uuid=account_uuid,
            account=account,
            email=email,
            phone_enc=phone_enc,
            is_exlucde_uuid=False,
        )

        t = ta(
            account_uuid=account_uuid,
            account=account,
            nickname=params.nickname,
            avatar_url=params.avatar_url,
            account_status=params.account_status,
            email=email,
            phone_enc=phone_enc,
            password_hash=password_hash,
            created_by=actor.account_uuid,
            updated_by=actor.account_uuid,

        )

        session.add(t)
        await session.flush()

        data = RespCreateAccount(account_uuid=account_uuid)
        return data

    @staticmethod
    async def get_account_list(
        actor: Actor,
        pagination: Pagination,
        nickname: str | None = None,
        account: str | None = None,
        account_status: AccountStatusOpts | None = None
    ) -> PaginationData:
        # 模糊匹配
        whereclause_args = [
            field.icontains(value) for value, field in [
                (nickname, ta.nickname),
                (account, ta.account)
            ] if value]

        # 精准匹配
        if account_status is not None:
            whereclause_args.append(ta.account_status == account_status.value)

        stmt = select(
            ta.account_uuid,
            ta.account,
            ta.nickname,
            ta.avatar_url,
            ta.phone_enc,
            ta.email,
            ta.account_status,
            ta.created_at
        ).where(
            *whereclause_args
        )

        # 根据创建时间倒序排序
        data = await ORM.pagination(
            actor.session,
            stmt,
            pagination,
            order_by_args=[ta.created_at.desc()]
        )

        # 用phoneMasked替代phone_enc
        for item in data.items:
            item["phone_masked"] = SecurityUtils.phone_decrypt(
                item["phone_enc"])

        return data
