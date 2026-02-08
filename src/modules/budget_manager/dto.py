from dataclasses import dataclass

from src.modules.commons import SourcePipeline


@dataclass(frozen=True, slots=True)
class InputBudgetManagerDTO: ...


CurrentBudgetPerPipeline = dict[SourcePipeline, int]


@dataclass(frozen=True, slots=True)
class OutputCurrentBudgetDTO:
    current_global_budget_usage: int
    current_pipeline_budget_usage: CurrentBudgetPerPipeline
