from src.modules.cost_engine.application.ports import CostEnginePort


class CostEngineAdapter(CostEnginePort):
    def execute(self, data):
        # concrete implementation
        ...
