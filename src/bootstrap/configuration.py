from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True


class PolicySettings(BaseModel):
    soft_usage_limit: float = 0.80
    hard_usage_limit: float = 0.95
    global_token_limit: int = 100_000
    pipeline_token_limit: int = 25_000


class Settings(BaseSettings):
    server: ServerSettings = ServerSettings()
    policy: PolicySettings = PolicySettings()

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__", case_sensitive=False)
