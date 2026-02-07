from dependency_injector import containers, providers

from src.modules.admission.use_case import AdmitLLMRequestUseCase
from src.modules.policy.service import DefaultPolicyService
from src.modules.validation.service import RequestValidationService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    wiring_config = containers.WiringConfiguration(packages=["src.api"])
    request_validator_service = providers.Factory(
        RequestValidationService,
    )
    policy_service = providers.Factory(
        DefaultPolicyService,
        global_token_limit=config.policy.global_token_limit,
        pipeline_token_limit=config.policy.pipeline_token_limit,
        hard_usage_limit=config.policy.hard_usage_limit,
        soft_usage_limit=config.policy.soft_usage_limit,
    )

    process_request = providers.Factory(
        AdmitLLMRequestUseCase, request_validator=request_validator_service, policy_service=policy_service
    )
