from dataclasses import dataclass

from src.modules.commons import Priority
from src.modules.policy.dto import PolicyDecision

LOW_PRIORITY_REQUESTS = (Priority.P1, Priority.P2)


class Budget:
    def __init__(
        self, total_limit: int, tokens_used: int, hard_usage_limit: float, soft_usage_limit: float
    ):
        self.total_limit = total_limit
        self.tokens_used = tokens_used
        self.hard_usage_limit = hard_usage_limit
        self.soft_usage_limit = soft_usage_limit

    def evaluate_request(self, estimated_tokens: int, priority: Priority) -> PolicyDecision:
        """
        Evaluate request against single budget
        """
        tokens_used_after_request = self.tokens_used + estimated_tokens
        percentage_of_tokens_used_after_request = tokens_used_after_request / self.total_limit

        if percentage_of_tokens_used_after_request > self.hard_usage_limit:
            return PolicyDecision.REJECT

        if percentage_of_tokens_used_after_request > self.soft_usage_limit and priority in LOW_PRIORITY_REQUESTS:
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
        if global_decision == PolicyDecision.REJECT:
            return PolicyDecision.REJECT  # TODO: verify with business

        pipeline_decision = self.pipeline_budget.evaluate_request(tokens, priority)
        return self._resolve_priority(global_decision, pipeline_decision)

    def _resolve_priority(self, d1: PolicyDecision, d2: PolicyDecision) -> PolicyDecision:
        """
        Select more strict decision.
        """
        order = {PolicyDecision.REJECT: 0, PolicyDecision.ALLOW_DEGRADED: 1, PolicyDecision.ALLOW: 2}
        return d1 if order[d1] < order[d2] else d2
