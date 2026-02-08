from src.modules.admission import AdmitLLMRequestUseCaseInputDTO, AdmitLLMRequestUseCaseOutputDTO
from src.modules.policy import BasePolicyService, InputPolicyServiceDTO
from src.modules.validation import BaseRequestValidationService


class AdmitLLMRequestUseCase:
    def __init__(self, request_validator: BaseRequestValidationService, policy_service: BasePolicyService):
        self._request_validator = request_validator
        self._policy_service = policy_service

    async def execute(self, dto: AdmitLLMRequestUseCaseInputDTO) -> AdmitLLMRequestUseCaseOutputDTO:
        await self._request_validator.validate(dto)
        policy_response = await self._policy_service.execute(_map_use_case_dto_to_policy_service_dto(dto))
        return AdmitLLMRequestUseCaseOutputDTO(decision=policy_response.decision)


def _map_use_case_dto_to_policy_service_dto(
    use_case_dto: AdmitLLMRequestUseCaseInputDTO,
) -> InputPolicyServiceDTO:
    return InputPolicyServiceDTO(
        estimated_tokens=use_case_dto.estimated_tokens,
        priority=use_case_dto.priority,
        pipeline=use_case_dto.pipeline,
    )
