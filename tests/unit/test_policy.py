import pytest

from src.modules.commons import PolicyDecision, Priority
from src.modules.policy.domain import Budget, PolicyContext

GLOBAL_TOTAL = 1_000_000
PIPELINE_TOTAL = 250_000
SOFT_LIMIT = 0.70
HARD_LIMIT = 0.90
P0_ALLOWANCE = 0.20
WHALE_THRESHOLD = 0.20
AVERAGE_TOKEN_AMOUNT = 40_000


@pytest.mark.parametrize(
    "estimated_tokens, priority, global_used, pipeline_used, expected_decision",
    [
        pytest.param(
            AVERAGE_TOKEN_AMOUNT,
            Priority.P1,
            0,
            0,
            PolicyDecision.ALLOW,
            id="Small P1 request, pipeline and global usage low",
        ),
        pytest.param(
            AVERAGE_TOKEN_AMOUNT,
            Priority.P0,
            0,
            0,
            PolicyDecision.ALLOW,
            id="Small P0 request, pipeline and global usage low",
        ),
        pytest.param(
            AVERAGE_TOKEN_AMOUNT,
            Priority.P2,
            699_000,
            0,
            PolicyDecision.ALLOW_DEGRADED,
            id="P2 request exceeds global soft limit",
        ),
        pytest.param(
            AVERAGE_TOKEN_AMOUNT,
            Priority.P1,
            0,
            175000,
            PolicyDecision.ALLOW_DEGRADED,
            id="P1 request exceeds pipeline soft limit",
        ),
        pytest.param(
            AVERAGE_TOKEN_AMOUNT, Priority.P0, 750_000, 187_500, PolicyDecision.ALLOW, id="P0 request, global soft limit exceeded"
        ),
        pytest.param(
            AVERAGE_TOKEN_AMOUNT, Priority.P1, 890_000, 0, PolicyDecision.REJECT, id="P1 request exceeds global hard limit "
        ),
        pytest.param(
            AVERAGE_TOKEN_AMOUNT,
            Priority.P2,
            300_000,
            212_500,
            PolicyDecision.REJECT,
            id="P2 request exceeds pipeline hard limit ",
        ),
        pytest.param(
            AVERAGE_TOKEN_AMOUNT,
            Priority.P0,
            1_000_000,
            225_000,
            PolicyDecision.ALLOW,
            id="P0 exceeds limit but uses additional allowance",
        ),
        pytest.param(
            1_200_000, Priority.P0, 0, 0, PolicyDecision.REJECT, id="Single request significantly too big"
        ),
    ],
)
def test_policy_scenarios(
    estimated_tokens: int,
    priority: Priority,
    global_used: int,
    pipeline_used: int,
    expected_decision: PolicyDecision,
):
    global_budget = Budget(
        total_limit=GLOBAL_TOTAL,
        tokens_used=global_used,
        soft_usage_limit=SOFT_LIMIT,
        hard_usage_limit=HARD_LIMIT,
    )
    pipeline_budget = Budget(
        total_limit=PIPELINE_TOTAL,
        tokens_used=pipeline_used,
        soft_usage_limit=SOFT_LIMIT,
        hard_usage_limit=HARD_LIMIT,
    )
    context = PolicyContext(
        global_budget=global_budget,
        pipeline_budget=pipeline_budget,
        whale_global_threshold=WHALE_THRESHOLD,
        whale_pipeline_threshold=WHALE_THRESHOLD,
        additional_p0_allowance=P0_ALLOWANCE,
    )
    actual_decision = context.decide(estimated_tokens, priority)

    assert actual_decision == expected_decision
