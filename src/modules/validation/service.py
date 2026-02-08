import hashlib

from cachetools import TTLCache

from src.modules.admission.dto import AdmitLLMRequestUseCaseInputDTO
from src.modules.validation.exceptions import RetryLimitExceededException
from src.modules.validation.interface import BaseRequestValidationService


class DefaultRequestValidationService(BaseRequestValidationService):
    def __init__(self):
        self._max_retries = 3
        self._cache_time_to_live = 5 * 60  # 5 minutes
        self._retry_tracker = TTLCache(maxsize=10_000, ttl=self._cache_time_to_live)

    def validate(self, dto: AdmitLLMRequestUseCaseInputDTO) -> None:
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
        payload = f"{dto.pipeline}-{dto.priority}-{dto.estimated_tokens}"
        return hashlib.md5(payload.encode()).hexdigest()