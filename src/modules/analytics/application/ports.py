from abc import ABC, abstractmethod


class AnalyticsPort(ABC):
    @abstractmethod
    def execute(self, data): ...
