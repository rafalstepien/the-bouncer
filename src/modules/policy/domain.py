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
        """
        Evaluate request against single budget
        """
        tokens_used_after_request = self.tokens_used + estimated_tokens
        percentage_of_tokens_used_after_request = tokens_used_after_request / self.total_limit
        if percentage_of_tokens_used_after_request > self.hard_usage_limit + additional_p0_allowance:
            return PolicyDecision.REJECT

        if (
            percentage_of_tokens_used_after_request > self.hard_usage_limit
            and priority in LOW_PRIORITY_REQUESTS
        ):
            return PolicyDecision.REJECT

        if (
            percentage_of_tokens_used_after_request > self.soft_usage_limit
            and priority in LOW_PRIORITY_REQUESTS
        ):
            return PolicyDecision.ALLOW_DEGRADED

        return PolicyDecision.ALLOW


@dataclass(frozen=True, slots=True)
class PolicyContext:
    global_budget: Budget
    pipeline_budget: Budget
    whale_global_threshold: float
    whale_pipeline_threshold: float
    additional_p0_allowance: float

    def decide(self, estimated_tokens_usage: int, priority: Priority) -> PolicyDecision:
        """
        Check for requests that take significant amount of tokens in single call (whale).
        Check global and then individual pipeline policy to decide whether to allow request.
        """
        if self._is_whale_request(estimated_tokens_usage):
            _LOGGER.warning("Whale request attempt rejected with {} tokens, while capacity is {}")
            return PolicyDecision.REJECT

        global_decision = self.global_budget.evaluate_request(
            estimated_tokens_usage, priority, self.additional_p0_allowance
        )
        if global_decision == PolicyDecision.REJECT:
            return PolicyDecision.REJECT  # TODO: verify with business

        pipeline_decision = self.pipeline_budget.evaluate_request(
            estimated_tokens_usage, priority, self.additional_p0_allowance
        )
        return self._resolve_priority(global_decision, pipeline_decision)

    def _resolve_priority(self, d1: PolicyDecision, d2: PolicyDecision) -> PolicyDecision:
        """
        Select more strict decision.
        """
        order = {PolicyDecision.REJECT: 0, PolicyDecision.ALLOW_DEGRADED: 1, PolicyDecision.ALLOW: 2}
        return d1 if order[d1] < order[d2] else d2

    def _is_whale_request(self, estimated_tokens_usage: int) -> bool:
        return (
            estimated_tokens_usage / self.global_budget.total_limit >= self.whale_global_threshold
            or estimated_tokens_usage / self.pipeline_budget.total_limit >= self.whale_pipeline_threshold
        )
