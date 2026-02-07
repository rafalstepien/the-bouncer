from dataclasses import dataclass

from src.modules.commons import PolicyDecision, Priority, SourcePipeline


@dataclass(slots=True, frozen=True)
class InputPolicyServiceDTO:
    estimated_tokens: int
    pipeline: SourcePipeline
    priority: Priority


@dataclass(slots=True, frozen=True)
class OutputPolicyServiceDTO:
    decision: PolicyDecision
