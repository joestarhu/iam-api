from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from core.config import settings
from core.routers import routers
from core.errors import BizError
from core.schemas import APIResponse

app = FastAPI(**settings.fastapi_kwargs)
app.add_middleware(CORSMiddleware, **settings.cors_kwargs)
app.include_router(routers)


@app.exception_handler(BizError)
async def hanle_biz_error(req: Request, exc: BizError) -> JSONResponse:
    """BizError的全局统一处理"""
    content = APIResponse(
        code=exc.code,
        message=exc.message,
        data=exc.data
    ).model_dump()

    return JSONResponse(status_code=200, content=content)


@app.exception_handler(HTTPException)
async def handle_http_exception(req: Request, exc: HTTPException) -> JSONResponse:
    content = APIResponse(
        code=exc.status_code,
        message=exc.detail,
        data=None
    ).model_dump()

    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )


@app.exception_handler(RequestValidationError)
async def handle_request_valid_error(req: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    messages = []

    for error in errors:
        loc = ".".join(str(item) for item in error.get("loc", []))
        msg = error.get("msg", "请求参数错误")
        if loc:
            messages.append(f"{loc}: {msg}")
        else:
            messages.append(msg)

    content = APIResponse(
        code=422,
        message="请求参数错误",
        data=messages
    ).model_dump()

    return JSONResponse(
        status_code=422,
        content=content
    )
