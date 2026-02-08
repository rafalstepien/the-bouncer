from dataclasses import dataclass
from typing import Callable

import aiohttp

from src.api.schemas import Priority
from tests.commons import APP_SETTINGS, CHUNK_SIZE, EVALUATE_URL


@dataclass
class TestCase:
    name: str
    description: str
    pipeline: str
    priority: Priority
    tokens: int
    expected_decision: str
    setup_function: Callable | None = None


async def fill_pipeline_to_percent(
    pipeline_name: str,
    target_percent: float,
):
    capacity = APP_SETTINGS.budget.pipeline_settings.max_capacity.get(pipeline_name, 0)
    tokens_needed = int(capacity * target_percent)
    async with aiohttp.ClientSession() as session:
        for _ in range(0, tokens_needed, CHUNK_SIZE):
            await session.post(
                EVALUATE_URL,
                json={
                    "pipeline": pipeline_name if pipeline_name != "global" else "monitoring",
                    "priority": "P0",
                    "estimated_tokens": CHUNK_SIZE,
                },
            )


async def fill_global_to_percent(target_percent):
    await fill_pipeline_to_percent("monitoring", target_percent)
    await fill_pipeline_to_percent("enrichment", target_percent)
    await fill_pipeline_to_percent("ranking", target_percent)
