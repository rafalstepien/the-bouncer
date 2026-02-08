from dependency_injector import containers, providers

from src.modules.admission.use_case import AdmitLLMRequestUseCase
from src.modules.budget_manager.service import DefaultBudgetManagerService
from src.modules.policy.service import DefaultPolicyService
from src.modules.validation.service import DefaultRequestValidationService
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-8s %(asctime)s [%(name)s:%(lineno)d] %(message)s",
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

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    logging_config = providers.Resource(
        logging.config.dictConfig,
        config=LOGGING_CONFIG,
    )

    wiring_config = containers.WiringConfiguration(packages=["src.api"])
    logger = providers.Singleton(
        logging.getLogger, 
        name="app.core"
    )
    request_validator_service = providers.Factory(
        DefaultRequestValidationService,
    )
    budget_manager = providers.Singleton(
        DefaultBudgetManagerService,
        global_budget_max_capacity=config.budget.global_settings.max_capacity,
        pipeline_budget_max_capacity=config.budget.pipeline_settings.max_capacity,
        token_refill_interval_seconds=config.budget.token_refill_interval_seconds,
    )
    policy_service = providers.Factory(
        DefaultPolicyService,
        budget_manager=budget_manager,
        logger=logger,
        global_budget_max_capacity=config.budget.global_settings.max_capacity,
        pipeline_budget_max_capacity=config.budget.pipeline_settings.max_capacity,
        hard_usage_limit=config.policy.hard_usage_limit,
        soft_usage_limit=config.policy.soft_usage_limit,
        degraded_discount=config.policy.degraded_discount,
        whale_request_size=config.policy.whale_request_size,
    )

    process_request = providers.Factory(
        AdmitLLMRequestUseCase, request_validator=request_validator_service, policy_service=policy_service
    )
