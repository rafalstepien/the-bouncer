import threading
from datetime import datetime

from src.modules.budget_manager.dto import OutputCurrentBudgetDTO
from src.modules.budget_manager.interface import BaseBudgetManager
from src.modules.commons import SourcePipeline


class DefaultBudgetManagerService(BaseBudgetManager):
    """
    With each request checks the time elapsed from last budget refill.
    If elapsed time is greater than the threshold (token_refill_interval_seconds), then budget is refilled to max.

    global_budget_max_capacity: Max amount of the tokens that can be used by all pipelines together in time interval
    pipeline_budget_max_capacity: Max amount of the tokens that can be used by single pipeline in time interval
    token_refill_interval_seconds: Budget is refilled to maximum capacity every {token_refill_interval_seconds}
    """

    def __init__(
        self,
        global_budget_max_capacity: int,
        pipeline_budget_max_capacity: dict[str, int],
        token_refill_interval_seconds: int,
    ):
        self._global_budget_max_capacity = global_budget_max_capacity
        self._pipeline_budget_max_capacity = pipeline_budget_max_capacity
        self._token_refill_interval_seconds = token_refill_interval_seconds

        self._last_updated: datetime | None = None
        self._current_global_budget_usage: int = 0
        self._current_pipeline_budget_usage: dict[str, int] = {
            p: 0 for p in self._pipeline_budget_max_capacity
        }

        self._lock = threading.Lock()

    def get_current_budget_usage(self) -> OutputCurrentBudgetDTO:
        with self._lock:
            self._refill_tokens()
            return OutputCurrentBudgetDTO(
                current_global_budget_usage=self._current_global_budget_usage,
                current_pipeline_budget_usage=self._current_pipeline_budget_usage,
            )

    def update_usage(self, tokens_used: int, pipeline: SourcePipeline) -> None:
        self._current_global_budget_usage += tokens_used
        self._current_pipeline_budget_usage[pipeline] += tokens_used

    def _refill_tokens(self):
        """
        Check if time elapsed from last update exceeds the refill interval. If it does - reset the budget.
        """
        if self._last_updated is None:
            self._last_updated = datetime.now()
            return

        now = datetime.now()
        time_elapsed = (now - self._last_updated).total_seconds()
        if time_elapsed > self._token_refill_interval_seconds:
            self._current_global_budget_usage = 0
            self._current_pipeline_budget_usage = {p: 0 for p in self._pipeline_budget_max_capacity}
            self._last_updated = now
