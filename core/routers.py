from fastapi import APIRouter

from biz.account.api import api as account_api
from biz.auth.api import api as auth_api


routers = APIRouter()
for router, prefix, tags in [
    (auth_api, "/auth", ["身份认证"]),
    (account_api, "/account", ["账号服务"]),
]:
    routers.include_router(router, prefix=prefix, tags=tags)  # type:ignore
