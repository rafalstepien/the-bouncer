from abc import ABC, abstractmethod

from src.modules.policy.dto import InputPolicyServiceDTO, OutputPolicyServiceDTO


class BasePolicyService(ABC):
    @abstractmethod
    def execute(self, dto: InputPolicyServiceDTO) -> OutputPolicyServiceDTO: ...
