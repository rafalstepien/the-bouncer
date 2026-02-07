from abc import ABC, abstractmethod


class RequestValidatorPort(ABC):
    @abstractmethod
    def execute(self, request): ...
