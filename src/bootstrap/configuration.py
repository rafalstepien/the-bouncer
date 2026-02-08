from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True


class PolicySettings(BaseModel):
    soft_usage_limit: float = 0.80
    hard_usage_limit: float = 0.95
    degraded_discount: float = 0.5
    whale_request_size: float = 0.2  # if the single request uses at least 20% of the budget - reject it


class GlobalBudgetSettings(BaseModel):
    max_capacity: int = 1_000_000


class PipelineBudgetSettings(BaseModel):
    max_capacity: dict[str, int] = {
        "monitoring": 500_000,
        "enrichment": 300_000,
        "ranking": 200_000,
    }


class BudgetSettings(BaseModel):
    token_refill_interval_seconds: int = 15  # 60 * 60 * 24  # 1 day
    global_settings: GlobalBudgetSettings = GlobalBudgetSettings()
    pipeline_settings: PipelineBudgetSettings = PipelineBudgetSettings()


class Settings(BaseSettings):
    server: ServerSettings = ServerSettings()
    policy: PolicySettings = PolicySettings()
    budget: BudgetSettings = BudgetSettings()

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__", case_sensitive=False)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-8s %(asctime)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}
