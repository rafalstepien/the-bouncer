from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class Priority(StrEnum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class AdmissionDecision(StrEnum):
    ALLOW = "ALLOW"
    ALLOW_DEGRADED = "ALLOW_DEGRADED"
    REJECT = "REJECT"
    ERROR = "ERROR"


class AdmissionRequest(BaseModel):
    pipeline: str
    priority: Priority
    estimated_tokens: int
    request_id: str | None = None


class AdmissionResponse(BaseModel):
    decision: AdmissionDecision
    context: dict[str, Any] | None = None
