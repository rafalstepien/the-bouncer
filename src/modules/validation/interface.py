from abc import ABC, abstractmethod

from src.modules.admission.dto import AdmitLLMRequestUseCaseInputDTO


class BaseRequestValidationService(ABC):
    @abstractmethod
    async def validate(self, dto: AdmitLLMRequestUseCaseInputDTO) -> None: ...
