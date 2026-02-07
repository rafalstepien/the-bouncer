from src.modules.policy.domain import Budget, PolicyContext
from src.modules.policy.dto import InputPolicyServiceDTO, OutputPolicyServiceDTO
from src.modules.policy.interface import BasePolicyService


class DefaultPolicyService(BasePolicyService):
    def __init__(
        self,
        global_token_limit: int,
        pipeline_token_limit: int,
        soft_usage_limit: float,
        hard_usage_limit: float,
    ):
        self._global_token_limit = global_token_limit
        self._pipeline_token_limit = pipeline_token_limit
        self._soft_usage_limit = soft_usage_limit
        self._hard_usage_limit = hard_usage_limit

    def execute(self, dto: InputPolicyServiceDTO) -> OutputPolicyServiceDTO:
        # state = self.repository.get_current_usage()
        state = {
            "global_tokens_used": 70_000,
            "pipelines_tokens_used": {
                "monitoring": 20_000,
                "enrichment": 50_000,
            },
        }

        context = PolicyContext(
            global_budget=Budget(
                total_limit=self._global_token_limit,
                current_usage=state["global_tokens_used"],
                soft_usage_limit=self._soft_usage_limit,
                hard_usage_limit=self._hard_usage_limit,
            ),
            pipeline_budget=Budget(
                total_limit=self._pipeline_token_limit,
                current_usage=state["pipelines_tokens_used"][dto.pipeline],
                soft_usage_limit=self._soft_usage_limit,
                hard_usage_limit=self._hard_usage_limit,
            ),
        )
        decision = context.decide(dto.estimated_tokens, dto.priority)
        return OutputPolicyServiceDTO(decision=decision)
