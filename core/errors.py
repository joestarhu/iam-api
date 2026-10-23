from typing import Any
from enum import Enum


class APIError(Enum):
    # 访问认证体系错误 1000~1099
    AUTH_ERR_PASSWORD_LOGIN = (1001, "账号或密码错误")
    AUTH_ERR_ACCOUNT_DISABLED = (1002, "账号已被停用")

    # ACCOUNT_LOGIN_TOO_MANY_TIMES = (1003, "账号多次密码登录失败")
    # DINGTALK_OAUTH_GET_USER_ERROR = (1004, "钉钉OAuth获取用户信息失败")
    # FEISHU_OAUTH_GET_USER_ERROR = (1005, "飞书OAuth获取用户信息失败")

    # 用户管理错误 1100~1199
    ACCOUNT_ERR_UNIQUE = (1100, "账号唯一性检测未通过")
    ACCOUNT_ERR_NOT_FOUND = (1101, "账号不存在")

    # USER_UUID_EXISTS = (1100, "用户UUID已存在")
    # ACCOUNT_UUID_EXISTS = (1100, "账号UUID已存在")
    # ACCOUNT_EXISTS = (1101, "用户账号已存在")
    # PHONE_EXISTS = (1102, "用户手机号已存在")
    # EMAIL_EXISTS = (1103, "用户邮箱已存在")
    # AUTH_TYPE_EXISTS = (1104, "用户认证类型已存在")
    # USER_NOT_FOUND = (1105, "用户不存在")

    # 应用管理 1200~1299

    # APP_UUID_EXISTS = (1200, "应用UUID已存在")
    # APP_NOT_FOUND = (1201, "应用不存在")
    # APP_RESOURCE_EXISTS = (1202, "应用资源已存在")
    # APP_ROLE_EXISTS = (1203, "应用角色已存在")

    @property
    def code(self) -> int:
        return self.value[0]

    @property
    def message(self) -> str:
        return self.value[1]


class BizError(Exception):
    def __init__(self, error: APIError, data: Any | None = None) -> None:
        self.error = error
        self.data = data
        super().__init__(error.message)

    @property
    def code(self) -> int:
        return self.error.code

    @property
    def message(self) -> str:
        return self.error.message
