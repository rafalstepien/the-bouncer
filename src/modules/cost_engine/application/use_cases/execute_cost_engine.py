from src.modules.cost_engine.application.ports import CostEnginePort


class ExecuteCostEngine:
    def __init__(self, port: CostEnginePort):
        self._port = port

    def execute(self, data):
        return self._port.execute(data)
