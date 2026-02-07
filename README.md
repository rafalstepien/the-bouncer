# the-bouncer
<img width="350" height="350" alt="image" src="https://github.com/user-attachments/assets/5bd17350-9a1f-4776-bc84-ff65f2223c44" />

## Limitations
These things are possible as future extensions, but won't be implemented, because in the description, the service is expected to be "small" and there are time limit constraints.

### Analytics collection 
Metrics should be emited via HTTP to some aggregation service (eg. Prometheus) and later visualized (eg. Grafana).

**Decision:** TBA

### Counting consumed tokens
We have two options to verify consumed tokens:
  - Option 1: Based only on estimated tokens. Prioritizes efficiency (simpler and faster system). 
  - Option 2: Based on estimated tokens + later updated by the actual number of tokens used. Requires pipelines to send additional data, requires the service to have additional endpoints, minimizes the risk of over/under estimation. 

**Decision:** Verification will be based only on estimated tokens with a room for extension later (addressing "Failure thinking: token estimates are wrong") from the requirements. From the description I assume that the business goal is mainly to prevent unexpected spikes of costs and not counting the exact number of tokens consumed. Until we keep estimates good enough, we don't have to complicate system with additional dependencies and prioritize faster development, simpler onboarding and less infrastructure overhead.

### Additional sophisticated mechanisms
There is a room for "competing" mechanism, for example if the global budget is exhausted, `P0` request comes in, and other, low-prio requests are still running (`P1`, `P2`), then the service could kill/revoke running requests.
There is a room for "borrowing" mechanism, for example if the budget of "monitoring" is exhausted, but "enrichment" has free tokens to use, then "monitoring" could use "enrichment" budget.

**Decision:** I will not implement those mechanisms, but I will leave the room for implementation in the future. It's good to think about the possible future use cases, but the task does not explicitly state any of such problems for now. There are more "optimization strategies", but the decision can be made later if we implement the service and spot some inefficiencies.

### Pipeline hierarchy
I noticed, that some pipelines can be more important than others. For example "monitoring" could be more important than "ranking", because it's more important to have better visibility into how tenders change instead of displaying them in correct order in the UI. In other words: not detecting a change in requirement of tender that is in progress is more serious than displaying "10 good fitting tenders for your company" in incorrect order.

**Decision:** Priority (P0/P1/P2) is the only ordering mechanism.


### What to do with degraded response 
**Decision:** What to do with `ALLOW_DEGRADED` service response will be made in the pipelines. Service does not care if pipeline will use cheaper model or shorter prompt.


### What to do when the service is down
We have two options there:
  - Option 1: Fail open. Pipelines send requests without the service as midddleman (priority: continuity of work). Disadvantage: we may exceed the budget and don't know about it.
  - Option 2: Fail closed. Pipelines can't send any request without the service (priority: budget safety). Disadvantage: when the service is down, pipelines can't process.

**Decision:** TBA


## Scenarios considered
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

