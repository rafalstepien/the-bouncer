import logging
from dataclasses import dataclass

from src.modules.commons import Priority
from src.modules.policy.dto import PolicyDecision

LOW_PRIORITY_REQUESTS = (Priority.P1, Priority.P2)
HIGH_PRIORITY_REQUESTS = (Priority.P0,)


_LOGGER = logging.getLogger()


class Budget:
    def __init__(self, total_limit: int, tokens_used: int, hard_usage_limit: float, soft_usage_limit: float):
        self.total_limit = total_limit
        self.tokens_used = tokens_used
        self.hard_usage_limit = hard_usage_limit
        self.soft_usage_limit = soft_usage_limit

    def evaluate_request(
        self, estimated_tokens: int, priority: Priority, additional_p0_allowance: float
    ) -> PolicyDecision:
        current_usage_ratio = (self.tokens_used + estimated_tokens) / self.total_limit

        if priority == Priority.P0:
            if current_usage_ratio <= (1.0 + additional_p0_allowance):
                return PolicyDecision.ALLOW
            return PolicyDecision.REJECT

        if current_usage_ratio > self.hard_usage_limit:
            return PolicyDecision.REJECT

        if current_usage_ratio > self.soft_usage_limit:
            return PolicyDecision.ALLOW_DEGRADED

        return PolicyDecision.ALLOW


@dataclass(frozen=True, slots=True)
class PolicyContext:
    global_budget: Budget
    pipeline_budget: Budget
    whale_threshold_tokens: float
    additional_p0_allowance: float

    def decide(self, estimated_tokens_usage: int, priority: Priority) -> PolicyDecision:
        if estimated_tokens_usage > self.whale_threshold_tokens:
            _LOGGER.warning(f"Whale request rejected: {estimated_tokens_usage} tokens exceeds threshold.")
            return PolicyDecision.REJECT

        global_decision = self.global_budget.evaluate_request(
            estimated_tokens_usage, priority, self.additional_p0_allowance
        )
        if global_decision == PolicyDecision.REJECT:
            return PolicyDecision.REJECT

        pipeline_decision = self.pipeline_budget.evaluate_request(
            estimated_tokens_usage, priority, self.additional_p0_allowance
        )

        return self._resolve_strictest(global_decision, pipeline_decision)

    def _resolve_strictest(self, d1: PolicyDecision, d2: PolicyDecision) -> PolicyDecision:
        order = {PolicyDecision.REJECT: 0, PolicyDecision.ALLOW_DEGRADED: 1, PolicyDecision.ALLOW: 2}
        return d1 if order[d1] < order[d2] else d2
