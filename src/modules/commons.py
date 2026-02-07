from enum import StrEnum


class Priority(StrEnum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class SourcePipeline(StrEnum):
    INGESTION = "ingestion"
    ENRICHMENT = "enrichment"
    MONITORING = "monitoring"
    RANKING = "ranking"


class PolicyDecision(StrEnum):
    ALLOW = "ALLOW"
    ALLOW_DEGRADED = "ALLOW_DEGRADED"
    REJECT = "REJECT"
