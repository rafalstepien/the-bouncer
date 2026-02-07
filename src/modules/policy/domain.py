from dataclasses import dataclass

from src.modules.commons import Priority
from src.modules.policy.dto import PolicyDecision

LOW_PRIORITY_REQUESTS = (Priority.P1, Priority.P2)


class Budget:
    def __init__(
        self, total_limit: int, current_usage: int, hard_usage_limit: float, soft_usage_limit: float
    ):
        self.total_limit = total_limit
        self.current_usage = current_usage
        self.hard_usage_limit = hard_usage_limit
        self.soft_usage_limit = soft_usage_limit

    def evaluate_request(self, estimated_tokens: int, priority: Priority) -> PolicyDecision:
        """
        Evaluate request against single budget
        """
        new_usage = self.current_usage + estimated_tokens
        usage_ratio = new_usage / self.total_limit

        if usage_ratio > self.hard_usage_limit:
            return PolicyDecision.REJECT

        if usage_ratio > self.soft_usage_limit and priority in LOW_PRIORITY_REQUESTS:
            return PolicyDecision.ALLOW_DEGRADED

        return PolicyDecision.ALLOW


@dataclass(frozen=True, slots=True)
class PolicyContext:
    global_budget: Budget
    pipeline_budget: Budget

    def decide(self, tokens: int, priority: Priority) -> PolicyDecision:
        """
        Check global and then individual pipeline policy to decide whether to allow request.
        """
        global_decision = self.global_budget.evaluate_request(tokens, priority)
        print(f"{global_decision=}")
        if global_decision == PolicyDecision.REJECT:
            return PolicyDecision.REJECT  # TODO: verify with business

        pipeline_decision = self.pipeline_budget.evaluate_request(tokens, priority)
        print(f"{pipeline_decision=}")
        return self._resolve_priority(global_decision, pipeline_decision)

    def _resolve_priority(self, d1: PolicyDecision, d2: PolicyDecision) -> PolicyDecision:
        """
        Select more strict decision.
        """
        order = {PolicyDecision.REJECT: 0, PolicyDecision.ALLOW_DEGRADED: 1, PolicyDecision.ALLOW: 2}
        return d1 if order[d1] < order[d2] else d2
