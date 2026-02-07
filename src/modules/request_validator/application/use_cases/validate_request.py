from src.modules.request_validator.application.ports import RequestValidatorPort


class ExecuteValidateRequest:
    def __init__(self, port: RequestValidatorPort):
        self._port = port

    def execute(self, data):
        return self._port.execute(data)
