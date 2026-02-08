import asyncio
from functools import partial

import aiohttp

from src.api.schemas import AdmissionRequest, Priority
from tests.commons import APP_SETTINGS, CHUNK_SIZE, EVALUATE_URL
from tests.utils import TestCase, fill_global_to_percent, fill_pipeline_to_percent

NEAR_SOFT_LIMIT_PERCENTAGE = APP_SETTINGS.policy.soft_usage_limit - 0.01
NEAR_HARD_LIMIT_PERCENTAGE = APP_SETTINGS.policy.hard_usage_limit - 0.01


# If the budget is at its max, this is the number of tokens P0 requests can use additionally
MAX_ALLOWANCE_TOKENS_FOR_P0 = (
    APP_SETTINGS.budget.global_settings.max_capacity * APP_SETTINGS.policy.additional_p0_allowance
) - 1


SCENARIOS = [
    TestCase(
        name="Scenario 1",
        description="Low budget usage, low priority request",
        pipeline="monitoring",
        priority=Priority.P1,
        tokens=CHUNK_SIZE,
        expected_decision="ALLOW",
    ),
    TestCase(
        name="Scenario 2",
        description="Low budget usage, high priority request",
        pipeline="monitoring",
        priority=Priority.P0,
        tokens=CHUNK_SIZE,
        expected_decision="ALLOW",
    ),
    TestCase(
        name="Scenario 3",
        description="Global usage at 84%, P1 request increases usage to 86% (soft limit crossed).",
        pipeline="enrichment",
        priority=Priority.P1,
        tokens=CHUNK_SIZE,
        expected_decision="ALLOW_DEGRADED",
        setup_function=partial(fill_global_to_percent, NEAR_SOFT_LIMIT_PERCENTAGE),
    ),
    TestCase(
        name="Scenario 4",
        description="Pipeline usage near soft limit (84%), P2 request crosses pipeline soft limit but global is fine.",
        pipeline="enrichment",
        priority=Priority.P2,
        tokens=CHUNK_SIZE,
        expected_decision="ALLOW_DEGRADED",
        setup_function=partial(fill_pipeline_to_percent, "enrichment", NEAR_SOFT_LIMIT_PERCENTAGE),
    ),
    TestCase(
        name="Scenario 5",
        description="Global & Pipeline both cross soft limit, but P0 is allowed full access.",
        pipeline="monitoring",
        priority=Priority.P0,
        tokens=CHUNK_SIZE,
        expected_decision="ALLOW",
        setup_function=partial(fill_global_to_percent, NEAR_SOFT_LIMIT_PERCENTAGE),
    ),
    TestCase(
        name="Scenario 6",
        description="Global usage at 94%, P1 request would cross 95% hard limit.",
        pipeline="ranking",
        priority=Priority.P1,
        tokens=CHUNK_SIZE,
        expected_decision="REJECT",
        setup_function=partial(fill_global_to_percent, NEAR_HARD_LIMIT_PERCENTAGE),
    ),
    TestCase(
        name="Scenario 7",
        description="Pipeline at 94%, P2 request would cross pipeline hard limit.",
        pipeline="monitoring",
        priority=Priority.P2,
        tokens=CHUNK_SIZE,
        expected_decision="REJECT",
        setup_function=partial(fill_pipeline_to_percent, "monitoring", NEAR_HARD_LIMIT_PERCENTAGE),
    ),
    TestCase(
        name="Scenario 8",
        description="P0 request allowed even if it exceeds hard limits (Safe-fail for critical traffic).",
        pipeline="enrichment",
        priority=Priority.P0,
        tokens=CHUNK_SIZE,
        expected_decision="ALLOW",
        setup_function=partial(fill_global_to_percent, NEAR_HARD_LIMIT_PERCENTAGE),
    ),
    TestCase(
        name="Scenario 9",
        description="Budget at max capacity, P0 request allowed if it exceeds budget within allowance",
        pipeline="enrichment",
        priority=Priority.P0,
        tokens=MAX_ALLOWANCE_TOKENS_FOR_P0,
        expected_decision="ALLOW",
        setup_function=partial(fill_global_to_percent, 1),
    ),
    TestCase(
        name="Scenario 10",
        description="Budget at max capacity, P0 request not allowed if it exceeds budget beyond allowance",
        pipeline="enrichment",
        priority=Priority.P0,
        tokens=MAX_ALLOWANCE_TOKENS_FOR_P0 + 1_000,
        expected_decision="REJECT",
        setup_function=partial(fill_global_to_percent, 1),
    ),
    TestCase(
        name="Scenario 11",
        description="Budget at max capacity, P1 request not allowed within P0 allowance",
        pipeline="enrichment",
        priority=Priority.P1,
        tokens=MAX_ALLOWANCE_TOKENS_FOR_P0,
        expected_decision="REJECT",
        setup_function=partial(fill_global_to_percent, 1),
    ),
    TestCase(
        name="Scenario 12",
        description="Whale Request: Single request > 10% of global capacity (100k).",
        pipeline="monitoring",
        priority=Priority.P0,
        tokens=CHUNK_SIZE + 300_000,
        expected_decision="REJECT",
    ),
    # TestCase(
    #     name="Scenario 10",
    #     description="Retry Storm: Logic to reject if metadata indicates excessive retries.",
    #     pipeline="ranking",
    #     priority=Priority.P1,
    #     tokens=1_000,
    #     expected_decision="REJECT",
    #     setup_function=setup_state__scenario_10 # Setup should inject retry headers/context
    # )
]


async def run_test(session: aiohttp.ClientSession, test_case: TestCase):
    if test_case.setup_function:
        await test_case.setup_function()

    payload = AdmissionRequest(
        pipeline=test_case.pipeline, priority=test_case.priority, estimated_tokens=test_case.tokens
    )
    async with session.post(EVALUATE_URL, json=payload.model_dump()) as resp:
        result = await resp.json()
        decision = result.get("decision")
        status = "✅ PASS" if decision == test_case.expected_decision else f"❌ FAIL (Got {decision})"
        print(f"{test_case.name} | {status}")
        return decision == test_case.expected_decision


async def main():
    async with aiohttp.ClientSession() as session:
        passed = 0
        for test_case in SCENARIOS:
            success = await run_test(session, test_case)
            if success:
                passed += 1

            await asyncio.sleep(APP_SETTINGS.budget.token_refill_interval_seconds + 5)
        print(f"Summary: {passed}/{len(SCENARIOS)} tests passed.")


if __name__ == "__main__":
    asyncio.run(main())
