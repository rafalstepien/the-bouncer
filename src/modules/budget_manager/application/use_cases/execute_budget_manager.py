from src.modules.budget_manager.application.ports import BudgetManagerPort


class ExecuteBudgetManager:
    def __init__(self, port: BudgetManagerPort):
        self._port = port

    def execute(self, data):
        return self._port.execute(data)
