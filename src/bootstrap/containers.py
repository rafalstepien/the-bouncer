from dependency_injector import containers, providers

from src.modules.analytics.infrastructure.analytics_adapter import AnalyticsAdapter
from src.modules.analytics.application.use_cases.execute_analytics import (
    ExecuteAnalytics,
)

from src.modules.cost_engine.infrastructure.cost_engine_adapter import CostEngineAdapter
from src.modules.cost_engine.application.use_cases.execute_cost_engine import (
    ExecuteCostEngine,
)

from src.modules.budget_manager.infrastructure.budget_manager_adapter import (
    BudgetManagerAdapter,
)
from src.modules.budget_manager.application.use_cases.execute_budget_manager import (
    ExecuteBudgetManager,
)

from src.modules.bouncer.application.use_cases.process_request import ProcessRequest


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["src.api"])

    # ---- Adapters (infrastructure) ----

    analytics_adapter = providers.Singleton(
        AnalyticsAdapter,
    )

    cost_engine_adapter = providers.Singleton(
        CostEngineAdapter,
    )

    budget_manager_adapter = providers.Singleton(
        BudgetManagerAdapter,
    )

    # ---- Use cases (application) ----

    analytics_use_case = providers.Factory(
        ExecuteAnalytics,
        port=analytics_adapter,
    )

    cost_engine_use_case = providers.Factory(
        ExecuteCostEngine,
        port=cost_engine_adapter,
    )

    budget_manager_use_case = providers.Factory(
        ExecuteBudgetManager,
        port=budget_manager_adapter,
    )

    # ---- Orchestrator (bouncer) ----

    process_request = providers.Factory(
        ProcessRequest,
        analytics=analytics_use_case,
        cost_engine=cost_engine_use_case,
        budget_manager=budget_manager_use_case,
    )
