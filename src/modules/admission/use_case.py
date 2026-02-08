from src.modules.admission.dto import AdmitLLMRequestUseCaseInputDTO, AdmitLLMRequestUseCaseOutputDTO
from src.modules.policy.interface import BasePolicyService
from src.modules.validation.interface import BaseRequestValidationService


class AdmitLLMRequestUseCase:
    def __init__(self, request_validator: BaseRequestValidationService, policy_service: BasePolicyService):
        self._request_validator = request_validator
        self._policy_service = policy_service

    async def execute(self, dto: AdmitLLMRequestUseCaseInputDTO) -> AdmitLLMRequestUseCaseOutputDTO:
        await self._request_validator.validate(dto)
        policy_response = await self._policy_service.execute(dto)
        return AdmitLLMRequestUseCaseOutputDTO(decision=policy_response.decision)
