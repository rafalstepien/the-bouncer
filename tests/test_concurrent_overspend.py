import asyncio
import threading

from src.modules.admission import AdmitLLMRequestUseCase, AdmitLLMRequestUseCaseInputDTO
from src.modules.budget_manager import InMemoryBudgetManager
from src.modules.commons import PolicyDecision
from src.modules.policy import DefaultPolicyService
from src.modules.validation import TestRequestValidationService

GLOBAL_BUDGET_MAX_CAPACITY = 100
PIPELINE_BUDGET_MAX_CAPACITY = 100


def run_sync_in_thread(use_case, dto, results, lock):
    """
    This function runs in a separate OS thread.
    It creates a local event loop to execute the async use case.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(use_case.execute(dto))
        with lock:
            results.append(result.decision)
    finally:
        loop.close()


async def test_budget_is_not_overspent_under_concurrency():
    """
    Verifies if the budget is vulnerable for overspend under high stress:
        - 30 threads are competing for the same budget
        - each request costs 30 tokens, while budget capacity is 100 tokens
        - no more than 3 requests should be allowed
    """
    request_validation_service = TestRequestValidationService()
    budget_manager = InMemoryBudgetManager(
        global_budget_max_capacity=GLOBAL_BUDGET_MAX_CAPACITY,
        pipeline_budget_max_capacity={"pipeline_a": PIPELINE_BUDGET_MAX_CAPACITY},
        token_refill_interval_seconds=60,
    )
    policy_service = DefaultPolicyService(
        budget_manager=budget_manager,
        global_budget_max_capacity=GLOBAL_BUDGET_MAX_CAPACITY,
        pipeline_budget_max_capacity={"pipeline_a": PIPELINE_BUDGET_MAX_CAPACITY},
        soft_usage_limit=0.5,
        hard_usage_limit=0.90,
        degraded_discount=1,
        whale_request_size=0.8,
        additional_p0_allowance=0,
    )
    dto = AdmitLLMRequestUseCaseInputDTO(
        pipeline="pipeline_a",
        priority="P1",
        estimated_tokens=30,
    )
    use_case = AdmitLLMRequestUseCase(
        request_validator=request_validation_service, policy_service=policy_service
    )

    results = []
    results_lock = threading.Lock()

    threads = [
        threading.Thread(target=run_sync_in_thread, args=(use_case, dto, results, results_lock))
        for _ in range(30)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    allowed = [r for r in results if r != PolicyDecision.REJECT]

    print(f"Total allowed: {len(allowed)}")
    assert len(allowed) <= 3


if __name__ == "__main__":
    asyncio.run(test_budget_is_not_overspent_under_concurrency())
