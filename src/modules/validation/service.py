import hashlib
from typing import Any

from cachetools import TTLCache

from src.modules.admission.dto import AdmitLLMRequestUseCaseInputDTO
from src.modules.validation.exceptions import RetryLimitExceededException
from src.modules.validation.interface import BaseRequestValidationService


class DefaultRequestValidationService(BaseRequestValidationService):
    def __init__(self, max_retries: int):
        self._max_retries = max_retries
        self._retry_tracker: TTLCache[str, Any] = TTLCache(maxsize=10_000, ttl=300)

    async def validate(self, dto: AdmitLLMRequestUseCaseInputDTO) -> None:
        self._handle_retry_loop(dto)

    def _handle_retry_loop(self, dto: AdmitLLMRequestUseCaseInputDTO) -> None:
        request_hash = self._get_request_hash(dto)
        current_attempts = self._retry_tracker.get(request_hash, 0) + 1
        self._retry_tracker[request_hash] = current_attempts

        if current_attempts > self._max_retries:
            raise RetryLimitExceededException(
                f"Executed more than {self._max_retries} retry attepmts for the same request in short time period. "
                "Short circuiting for safety reasons (pipeline could enter infinity loop)"
            )

    def _get_request_hash(self, dto: AdmitLLMRequestUseCaseInputDTO) -> str:
        payload = f"{dto.pipeline}-{dto.priority}-{dto.estimated_tokens}-{dto.request_id or ''}"
        return hashlib.md5(payload.encode()).hexdigest()


class TestRequestValidationService(BaseRequestValidationService):
    async def validate(self, dto: AdmitLLMRequestUseCaseInputDTO) -> None: ...
