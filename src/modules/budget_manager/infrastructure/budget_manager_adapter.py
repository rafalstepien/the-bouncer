from src.modules.budget_manager.application.ports import BudgetManagerPort


class BudgetManagerAdapter(BudgetManagerPort):
    def execute(self, data):
        # concrete implementation
        ...
