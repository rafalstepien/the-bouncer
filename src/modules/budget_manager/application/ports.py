from abc import ABC, abstractmethod


class BudgetManagerPort(ABC):
    @abstractmethod
    def execute(self, data): ...
