from abc import ABC, abstractmethod


class CostEnginePort(ABC):
    @abstractmethod
    def execute(self, data): ...
