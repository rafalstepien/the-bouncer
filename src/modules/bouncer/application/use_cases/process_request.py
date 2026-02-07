class ProcessRequest:
    def __init__(
        self,
        analytics,
        cost_engine,
        budget_manager,
    ):
        self._analytics = analytics
        self._cost_engine = cost_engine
        self._budget_manager = budget_manager

    def execute(self, request):
        self._analytics.execute(request)
        cost = self._cost_engine.execute(request)
        self._budget_manager.execute(cost)

        return cost
