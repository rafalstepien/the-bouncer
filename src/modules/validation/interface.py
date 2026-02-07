from abc import ABC, abstractmethod

from src.modules.admission.dto import AdmitLLMRequestUseCaseInputDTO


class BaseRequestValidationService(ABC):
    @abstractmethod
    def validate(self, dto: AdmitLLMRequestUseCaseInputDTO): ...
