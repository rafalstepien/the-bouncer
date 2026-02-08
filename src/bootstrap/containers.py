import logging.config

from dependency_injector import containers, providers

from src.bootstrap.configuration import LOGGING_CONFIG
from src.modules.admission import AdmitLLMRequestUseCase
from src.modules.budget_manager import InMemoryBudgetManager
from src.modules.policy import DefaultPolicyService
from src.modules.validation import DefaultRequestValidationService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    logging_config = providers.Resource(
        logging.config.dictConfig,
        config=LOGGING_CONFIG,
    )

    wiring_config = containers.WiringConfiguration(packages=["src.api"])
    request_validator_service = providers.Singleton(
        DefaultRequestValidationService,
        max_retries=config.policy.max_retries,
    )
    budget_manager = providers.Singleton(
        InMemoryBudgetManager,
        global_budget_max_capacity=config.budget.global_settings.max_capacity,
        pipeline_budget_max_capacity=config.budget.pipeline_settings.max_capacity,
        token_refill_interval_seconds=config.budget.token_refill_interval_seconds,
    )
    policy_service = providers.Factory(
        DefaultPolicyService,
        budget_manager=budget_manager,
        global_budget_max_capacity=config.budget.global_settings.max_capacity,
        pipeline_budget_max_capacity=config.budget.pipeline_settings.max_capacity,
        hard_usage_limit=config.policy.hard_usage_limit,
        soft_usage_limit=config.policy.soft_usage_limit,
        degraded_discount=config.policy.degraded_discount,
        whale_request_size=config.policy.whale_request_size,
        additional_p0_allowance=config.policy.additional_p0_allowance,
    )

    process_request = providers.Factory(
        AdmitLLMRequestUseCase, request_validator=request_validator_service, policy_service=policy_service
    )
