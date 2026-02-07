from src.modules.analytics.application.ports import AnalyticsPort
from src.modules.cost_engine.application.ports import CostEnginePort
from src.modules.budget_manager.application.ports import BudgetManagerPort

class ProcessRequest:
    def __init__(
        self,
        analytics: AnalyticsPort,
        cost_engine: CostEnginePort,
        budget_manager: BudgetManagerPort,
    ):
        self._analytics = analytics
        self._cost_engine = cost_engine
        self._budget_manager = budget_manager

    def execute(self, request):
        cost = self._cost_engine.execute(request)
        self._budget_manager.execute(cost)
        self._analytics.execute(request)
        return cost
