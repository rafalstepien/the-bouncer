from dependency_injector import containers, providers

from src.modules.admission.use_case import AdmitLLMRequestUseCase
from src.modules.budget_manager.service import DefaultBudgetManagerService
from src.modules.policy.service import DefaultPolicyService
from src.modules.validation.service import DefaultRequestValidationService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    wiring_config = containers.WiringConfiguration(packages=["src.api"])
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
        global_budget_max_capacity=config.budget.global_settings.max_capacity,
        pipeline_budget_max_capacity=config.budget.pipeline_settings.max_capacity,
        hard_usage_limit=config.policy.hard_usage_limit,
        soft_usage_limit=config.policy.soft_usage_limit,
        degraded_discount=config.policy.degraded_discount,
    )

    process_request = providers.Factory(
        AdmitLLMRequestUseCase, request_validator=request_validator_service, policy_service=policy_service
    )
