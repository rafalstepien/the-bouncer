from dataclasses import dataclass

from src.modules.commons import PolicyDecision, Priority, SourcePipeline


@dataclass(slots=True, frozen=True)
class AdmitLLMRequestUseCaseInputDTO:
    pipeline: SourcePipeline
    priority: Priority
    estimated_tokens: int
    request_id: str | None = None


@dataclass(slots=True, frozen=True)
class AdmitLLMRequestUseCaseOutputDTO:
    decision: PolicyDecision
