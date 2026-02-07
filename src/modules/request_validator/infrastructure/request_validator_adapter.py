from src.modules.request_validator.application.ports import RequestValidatorPort


class RequestValidatorAdapter(RequestValidatorPort):
    def execute(self, data):
        # concrete implementation
        ...
