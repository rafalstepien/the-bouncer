from abc import ABC, abstractmethod
from src.modules.budget_manager.dto import OutputCurrentBudgetDTO


class BaseBudgetManager(ABC):
    @abstractmethod
    def update_budget(self): ...

    @abstractmethod
    def get_current_budget_usage(self) -> OutputCurrentBudgetDTO: ...
