from src.modules.budget_manager.interface import BaseBudgetManager
from src.modules.policy.domain import Budget, PolicyContext
from src.modules.policy.dto import InputPolicyServiceDTO, OutputPolicyServiceDTO, PolicyDecision
from src.modules.policy.interface import BasePolicyService


class DefaultPolicyService(BasePolicyService):
    def __init__(
        self,
        budget_manager: BaseBudgetManager,
        global_budget_max_capacity: int,
        pipeline_budget_max_capacity: int,
        soft_usage_limit: float,
        hard_usage_limit: float,
        degraded_discount: float
    ):
        self._budget_manager = budget_manager
        self._global_budget_max_capacity = global_budget_max_capacity
        self._pipeline_budget_max_capacity = pipeline_budget_max_capacity
        self._soft_usage_limit = soft_usage_limit
        self._hard_usage_limit = hard_usage_limit
        self._degraded_discount = degraded_discount

    def execute(self, dto: InputPolicyServiceDTO) -> OutputPolicyServiceDTO:
        state = self._budget_manager.get_current_budget_usage()
        self._print_current_state(state)
        context = PolicyContext(
            global_budget=Budget(
                total_limit=self._global_budget_max_capacity,
                tokens_used=state.current_global_budget_usage,
                soft_usage_limit=self._soft_usage_limit,
                hard_usage_limit=self._hard_usage_limit,
            ),
            pipeline_budget=Budget(
                total_limit=self._pipeline_budget_max_capacity[dto.pipeline],
                tokens_used=state.current_pipeline_budget_usage[dto.pipeline],
                soft_usage_limit=self._soft_usage_limit,
                hard_usage_limit=self._hard_usage_limit,
            ),
        )
        decision = context.decide(dto.estimated_tokens, dto.priority)
        
        if decision == PolicyDecision.ALLOW:
            self._budget_manager.update_budget(dto.estimated_tokens, dto.pipeline)
        elif decision == PolicyDecision.ALLOW_DEGRADED:
            tokens_used = dto.estimated_tokens * self._degraded_discount
            self._budget_manager.update_budget(tokens_used, dto.pipeline)
        
        return OutputPolicyServiceDTO(decision=decision)
    
    def _print_current_state(self, state):
        print("--------")
        print(f"CURRENT GLOBAL BUDGET USAGE: {state.current_global_budget_usage * 100 / self._global_budget_max_capacity}%")
        print(f"CURRENT PIPELINE BUDGET USAGE")
        for p in self._pipeline_budget_max_capacity:
            print(f"{p}: {state.current_pipeline_budget_usage[p] * 100 / self._pipeline_budget_max_capacity[p]}%")
        print("--------")
