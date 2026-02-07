from src.modules.cost_engine.application.ports import Cost_enginePort


class CostEngineAdapter(Cost_enginePort):
    def execute(self, data):
        # concrete implementation
        ...
