from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from core.deps import get_sesion, get_actor
from core.utils import SecurityUtils
from core.schemas import APIResponse
from core.config import settings
from biz.auth.service import AuthService
from biz.auth.schema import ReqPasswordLogin, RespJWT, RespProfile

api = APIRouter()


@api.post("/login", summary="账密登录")
async def login(
    req: ReqPasswordLogin,
    session=Depends(get_sesion)
) -> APIResponse[RespJWT]:
    # 这里需要对password进行解密
    password = SecurityUtils.request_params_decrypt(req.password)

    data = await AuthService.password_login(req.account, password, session)
    return APIResponse(data=data)


@api.get("/profile", summary="获取用户账号信息")
async def get_profile(actor=Depends(get_actor)) -> APIResponse[RespProfile]:
    data = await AuthService.get_profile(actor)
    return APIResponse(data=data)


@api.get("/pub", summary="公钥信息")
async def get_public() -> APIResponse:
    data = settings.private_key.public_key().export_key().decode()
    return APIResponse(data=data)


@api.post("/docs-login", summary="Swagger登录用")
async def docs_login(
    req=Depends(OAuth2PasswordRequestForm),
    session=Depends(get_sesion)
) -> dict:
    data = await AuthService.password_login(req.username, req.password, session)
    return {"access_token": data.access_token, "token_type": "bearer"}
