from src.modules.analytics.application.ports import AnalyticsPort


class ExecuteAnalytics:
    def __init__(self, port: AnalyticsPort):
        self._port = port

    def execute(self, data):
        return self._port.execute(data)
