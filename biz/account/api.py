from fastapi import APIRouter, Depends, Security

from core.schemas import APIResponse, PaginationData, APIPermission
from core.deps import get_actor, get_pagination
from biz.account.schema import ReqCreateAccount, RespCreateAccount, ParamsCreateAccount, AccountStatusOpts, AccountListResponse
from biz.account.service import AccountService

api = APIRouter()

permissions = [
    CREATE := APIPermission("/create", "创建账号", "account:create"),
    EDIT := APIPermission("/create", "编辑账号", "account:edit"),
    DELETE := APIPermission("/delete", "删除账号", "account:delete"),

    LIST := APIPermission("/list", "获取账号列表", "account:list"),
    DETAIL := APIPermission("/list", "获取账号详情", "account:detail"),
]


@api.post(**CREATE.method_kwargs)
async def create_account(
    req: ReqCreateAccount,
    actor=Security(get_actor, scopes=[CREATE.scope])
) -> APIResponse[RespCreateAccount]:
    # Fixme("需要前端配合使用公钥加密,后端私钥解密")
    password = req.password_hash

    params = ParamsCreateAccount(
        password=password,
        **req.model_dump()
    )

    data = await AccountService.create_account(params, actor)
    return APIResponse(data=data)


@api.get(**LIST.method_kwargs)
async def get_account_list(
    nickname: str | None = None,
    account: str | None = None,
    account_status: AccountStatusOpts | None = None,
    pagination=Depends(get_pagination),
    actor=Security(get_actor, scopes=[LIST.scope])
) -> APIResponse[PaginationData[AccountListResponse]]:
    data = await AccountService.get_account_list(actor, pagination, nickname, account, account_status)
    return APIResponse(data=data)
