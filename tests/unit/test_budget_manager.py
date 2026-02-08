from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from src.modules.budget_manager.service import InMemoryBudgetManager
from src.modules.commons import SourcePipeline

PIPELINE_1 = "pipeline_1"
PIPELINE_2 = "pipeline_2"
GLOBAL_MAX = 1000
PIPELINE_MAX = {PIPELINE_1: 500, PIPELINE_2: 500}
INTERVAL = 60


@pytest.fixture
def budget_service():
    return InMemoryBudgetManager(
        global_budget_max_capacity=GLOBAL_MAX,
        pipeline_budget_max_capacity=PIPELINE_MAX,
        token_refill_interval_seconds=INTERVAL,
    )


@pytest.mark.parametrize(
    "tokens_to_add, pipeline, expected_global, expected_pipeline",
    [
        pytest.param(
            100, PIPELINE_1, 100, {PIPELINE_1: 100, PIPELINE_2: 0}, id="Update budget adds tokens correctly"
        ),
        pytest.param(
            0, PIPELINE_2, 0, {PIPELINE_1: 0, PIPELINE_2: 0}, id="Update budget handles zero tokens correctly"
        ),
    ],
)
def test_update_budget(
    budget_service: InMemoryBudgetManager,
    tokens_to_add: int,
    pipeline: SourcePipeline,
    expected_global: int,
    expected_pipeline: dict[str, int],
):
    budget_service.update_usage(tokens_to_add, pipeline)
    usage = budget_service.get_current_budget_usage()

    assert usage.current_global_budget_usage == expected_global
    assert usage.current_pipeline_budget_usage == expected_pipeline


def test_refill_logic_resets_after_interval(budget_service: InMemoryBudgetManager):
    initial_time = datetime(2024, 1, 1, 12, 0, 0)

    with patch("src.modules.budget_manager.service.datetime") as mock_datetime:
        mock_datetime.now.return_value = initial_time

        budget_service.get_current_budget_usage()
        budget_service.update_usage(500, PIPELINE_1)

        usage_before = budget_service.get_current_budget_usage()
        assert usage_before.current_global_budget_usage == 500

        mock_datetime.now.return_value = initial_time + timedelta(seconds=INTERVAL + 1)

        usage_after = budget_service.get_current_budget_usage()

        assert usage_after.current_global_budget_usage == 0
        assert usage_after.current_pipeline_budget_usage[PIPELINE_1] == 0
        assert budget_service._last_updated == initial_time + timedelta(seconds=INTERVAL + 1)


@pytest.mark.parametrize(
    "seconds_passed, should_refill",
    [
        pytest.param(30, False, id="No refill before interval elapsed"),
        pytest.param(61, True, id="Refill after interval elapsed"),
    ],
)
def test_refill_threshold_boundaries(
    budget_service: InMemoryBudgetManager, seconds_passed: int, should_refill: bool
):
    start_time = datetime(2024, 1, 1, 12, 0, 0)

    with patch("src.modules.budget_manager.service.datetime") as mock_datetime:
        mock_datetime.now.return_value = start_time
        budget_service.get_current_budget_usage()
        budget_service.update_usage(100, PIPELINE_1)

        mock_datetime.now.return_value = start_time + timedelta(seconds=seconds_passed)

        usage = budget_service.get_current_budget_usage()
        expected_usage = 0 if should_refill else 100
        assert usage.current_global_budget_usage == expected_usage


def test_initial_call_sets_last_updated(budget_service: InMemoryBudgetManager):
    assert budget_service._last_updated is None

    with patch("src.modules.budget_manager.service.datetime") as mock_datetime:
        fixed_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_now

        budget_service.get_current_budget_usage()

        assert budget_service._last_updated == fixed_now
