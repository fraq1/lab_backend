from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from pathlib import Path

class AccessTokenConfig(BaseModel):
    reset_password_token_secret: str
    verification_token_secret: str

class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

class AuthConfig(BaseModel):
    cookie_max_age: int = 3600
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

class DatabaseConfig(BaseModel):
    url: str
    echo: bool = True
    future: bool = True


class UrlPrefix(BaseModel):
    prefix: str = "/api"
    test: str = "/test"
    posts: str = "/posts"
    receipts: str = "/receipts"
    cuisines: str = "/cuisines"
    allergens: str = "/allergens"
    auth: str = "/auth"
    ingredients: str = "/ingredients"
    users: str = "/users"
    access_token: str = "/access_token"
    bearer_token_url: str = "/api/auth/login"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    url: UrlPrefix = UrlPrefix()
    db: DatabaseConfig
    access_token: AccessTokenConfig
    auth: AuthConfig = AuthConfig()


settings = Settings()
