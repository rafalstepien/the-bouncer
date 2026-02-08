
## Scenarios considered when designing the app

### Setup
- TOTAL_GLOBAL_BUDGET: 1,000,000
- TOTAL_SINGLE_PIPELINE_BUDGET: 250,000
- SOFT_LIMIT (when we start ALLOW_DEGRADED for P1/P2): 70%
- HARD_LIMIT (when we start to REJECT all or REJECT P1/P2): 90%

### Scenarios
SCENARIO 1: STABLE LOAD P1/P2
- global budget used in 0%, pipeline budget used in 0%
- P1/P2 request comes in with 50,000 tokens
- global ok, pipeline ok, priority low but the usage is low
- decision: ALLOW, allow budget safe

SCENARIO 2: STABLE LOAD P0
- global budget used in 0%, pipeline budget used in 0%
- P0 request comes in with 50,000 tokens
- global ok, pipeline ok, priority high
- decision: ALLOW, allow budget safe

SCENARIO 3: SUDDEN LOW PRIO BURST SOFT LIMIT AT GLOBAL LEVEL
- global budget used in 65%, pipeline budget used in 0%
- P1/P2 request comes in with 100,000 tokens
- global budget will be used (after the request) in 75% - soft limit exceeded
- decision: ALLOW_DEGRADED, because this is P1/P2

SCENARIO 4: SUDDEN LOW PRIO BURST SOFT LIMIT AT PIPELINE LEVEL
- global budget used in 0%, pipeline budget used in 0%
- P1/P2 request comes in with 200,000 tokens
- global ok, pipeline budget will be used (after the request) in 80% - soft limit exceeded
- decision: ALLOW_DEGRADED, because this is P1/P2

SCENARIO 5: SUDDEN HIGH PRIO BUST SOFT LIMIT ALLOWED
- global budget used in 75%, pipeline budget used in 75%
- P0 request comes in with 50,000 tokens
- global soft limit exceeded, pipeline soft limt exceeded
- decision: ALLOW, because this is P0

SCENARIO 6: SUDDEN LOW PRIO BURST HARD LIMIT AT GLOBAL LEVEL
- global budget used in 89%, pipeline budget used in 0%
- P1/P2 request comes in with 50,000 tokens
- global budget will be used (after the request) in 94% - hard limit exceeded
- decision: REJECT, because this is P1/P2

SCENARIO 7: SUDDEN LOW PRIO BURST HARD LIMIT AT PIPELINE LEVEL
- global budget used in 30%, pipeline budget used in 85%
- P1/P2 request comes in with 50,000 tokens
- global budget ok, pipeline budget will be used (after the request) in 94% - hard limit exceeded
- decision: REJECT, because this is P1/P2

SCENARIO 8: SUDDEN HIGH PRIO BUST HARD LIMIT ALLOWED
- global budget used in 90%, pipeline budget used in 90%
- P0 request comes in with 50,000 tokens
- global hard limit exceeded, pipeline hard limt exceeded
- decision: ALLOW, because this is P0

SCENARIO 9: WHALE REQUEST
- global budget used in 0%, pipeline budget used in 0%
- P0 request comes in with 1,200,000 tokens
- decision: REJECT

SCENARIO 10: RETRY STORM
- request is stuck in the retry loop and must be stopped at some point

