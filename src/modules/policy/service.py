import logging

from src.modules.budget_manager.interface import BaseBudgetManager
from src.modules.policy.domain import Budget, PolicyContext
from src.modules.policy.dto import InputPolicyServiceDTO, OutputPolicyServiceDTO, PolicyDecision
from src.modules.policy.interface import BasePolicyService

_LOGGER = logging.getLogger()


class DefaultPolicyService(BasePolicyService):
    def __init__(
        self,
        budget_manager: BaseBudgetManager,
        global_budget_max_capacity: int,
        pipeline_budget_max_capacity: dict[str, int],
        soft_usage_limit: float,
        hard_usage_limit: float,
        degraded_discount: float,
        whale_request_size: float,
        additional_p0_allowance: float,
    ):
        self._budget_manager = budget_manager
        self._global_budget_max_capacity = global_budget_max_capacity
        self._pipeline_budget_max_capacity = pipeline_budget_max_capacity
        self._soft_usage_limit = soft_usage_limit
        self._hard_usage_limit = hard_usage_limit
        self._degraded_discount = degraded_discount
        self._whale_request_size = whale_request_size
        self._additional_p0_allowance = additional_p0_allowance

    def execute(self, dto: InputPolicyServiceDTO) -> OutputPolicyServiceDTO:
        whale_threshold_tokens = self._whale_request_size * self._global_budget_max_capacity
        with self._budget_manager.with_lock():
            state = self._budget_manager.get_current_budget_usage()
            # self._log_current_state(state)
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
                whale_threshold_tokens=whale_threshold_tokens,
                additional_p0_allowance=self._additional_p0_allowance,
            )
            decision = context.decide(dto.estimated_tokens, dto.priority)

            if decision == PolicyDecision.ALLOW:
                self._budget_manager.update_usage(dto.estimated_tokens, dto.pipeline)
            elif decision == PolicyDecision.ALLOW_DEGRADED:
                tokens_used = dto.estimated_tokens * self._degraded_discount
                self._budget_manager.update_usage(tokens_used, dto.pipeline)

        return OutputPolicyServiceDTO(decision=decision)

    def _log_current_state(self, state):
        _LOGGER.info("-----------")
        _LOGGER.info(
            f"CURRENT GLOBAL BUDGET USAGE: {state.current_global_budget_usage * 100 / self._global_budget_max_capacity}%"
        )
        pipelines_usage = [
            f"{p}={state.current_pipeline_budget_usage[p] * 100 / self._pipeline_budget_max_capacity[p]}%"
            for p in self._pipeline_budget_max_capacity
        ]
        _LOGGER.info(f"CURRENT PIPELINE BUDGET USAGE: {pipelines_usage}")
