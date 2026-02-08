from abc import ABC, abstractmethod

from src.modules.budget_manager.dto import OutputCurrentBudgetDTO
from src.modules.commons import SourcePipeline


class BaseBudgetManager(ABC):
    @abstractmethod
    def update_usage(self, tokens_used: int, pipeline: SourcePipeline) -> None: ...

    @abstractmethod
    def get_current_budget_usage(self) -> OutputCurrentBudgetDTO: ...

    @abstractmethod
    def with_lock(self): ...
