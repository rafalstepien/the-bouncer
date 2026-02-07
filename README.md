# the-bouncer
<img width="350" height="350" alt="image" src="https://github.com/user-attachments/assets/5bd17350-9a1f-4776-bc84-ff65f2223c44" />

## Limitations
These things are possible as future extensions, but won't be implemented, because in the description, the service is expected to be "small" and there are time limit constraints.
- Analytics collection service: metrics will be emited to a simple log file, that we can parse. Separate metric aggregator UI can parse this file.
- Verification of consumed tokens is based solely on estimated number of tokens coming in the request. This optimizes efficiency, not accuracy. In the future we could extend the service to accept the actual number of computed tokens on separate endpoint, and make pipelines be able to send this information. This can minimize the risk of over/under estimation.
- There is a room for "competing" mechanism. **Example:** If the global budget is exhausted, `P0` request comes in, and other, low-prio requests are still running (`P1`, `P2`), then the service will can kill/revoke running requests.
- There is a room for "borrowing" mechanism. **Example:** If the budget of "monitoring" is exhausted, but "enrichment" has tokens to use, then "monitoring" could use "enrichment" budget.
- Pipeline hierarchy: some pipelines seem to be more important than others (eg. "monitoring" should be more important than "ranking", because if monitoring request is rejected we lose visibility, which feels more important than ordering in the UI). This will be always handled via priorities (P0/P1/P2).
- Decision what to do with `ALLOW_DEGRADED` service response should be made in the pipeline. Service does not care if pipeline will use cheaper model or shorter prompt.
- We have two decisions to make when `the-bouncer` is down:
  - Option 1: Fail open. Pipelines send requests without the service as midddleman (priority: continuity of work). Disadvantage: we may exceed the budget and don't know about it.
  - Option 2: Fail closed. Pipelines can't send any request without the service (priority: budget safety). Disadvantage: when the service is down, pipelines can't process.

## Scenarios
TOTAL_GLOBAL_BUDGET: 1,000,000
TOTAL_SINGLE_PIPELINE_BUDGET: 250,000
SOFT_LIMIT (when we start ALLOW_DEGRADED for P1/P2): 70%
HARD_LIMIT (when we start to REJECT all or REJECT P1/P2): 90%

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

