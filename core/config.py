from functools import lru_cache
from pathlib import Path


from pydantic import Field, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from Cryptodome.PublicKey import RSA


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # 本地环境变量文件
        env_file=".env",
        # 额外的环境变量处置: ignore就是忽略的意思
        extra="ignore",
        # env环境变量编码
        env_file_encoding="utf-8",
        # env参数前缀,避免环境变量污染
        env_prefix="IAM_",
    )

    # FastAPI参数
    title: str = "IAM"
    version: str = "1.0.0"
    docs_enable: bool = True
    redoc_enable: bool = True

    @property
    def fastapi_kwargs(self) -> dict:
        args = {
            "title": self.title,
            "version": self.version,
        }

        for arg_is_enable, arg_keyword in [
            (self.docs_enable, "docs_url"),
            (self.redoc_enable, "redoc_url"),
        ]:
            if not arg_is_enable:
                args |= {arg_keyword: None}

        return args

    # CORS参数
    allow_origins: list[str] = Field(default_factory=lambda: ["*"])
    allow_headers: list[str] = Field(default_factory=lambda: ["*"])
    allow_methods: list[str] = Field(default_factory=lambda: ["*"])
    allow_credentials: bool = True

    @property
    def cors_kwargs(self) -> dict:
        return {
            "allow_origins": self.allow_origins,
            "allow_headers": self.allow_headers,
            "allow_methods": self.allow_methods,
            "allow_credentials": self.allow_credentials,
        }

    # 数据库参数
    orm_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/schema"
    orm_echo: bool = False
    orm_pool_recycle: PositiveInt = 3600

    @property
    def orm_kwargs(self) -> dict:
        return {
            "url": self.orm_url,
            "echo": self.orm_echo,
            "pool_recycle": self.orm_pool_recycle
        }

    # JWT参数配置
    jwt_key: SecretStr = SecretStr(
        "Z79m30/nN9gGJSWbVaFDQIesXMVxnr38O1n91NmzPG4=")
    jwt_algorithm: str = "HS256"
    access_token_expire_min: PositiveInt = 60*24*7
    # refresh_token_expire_min: PositiveInt = 60*24*7

    # AES Key配置
    aes_ecb_key: SecretStr = SecretStr("j5TLpq7N1ydtZevTWOxhDw==")

    # 用于密码传输解密用的私钥地址
    password_sk_path: str = "private.pem"

    @property
    def private_key(self):
        return RSA.import_key(
            Path(self.password_sk_path).read_bytes()
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
