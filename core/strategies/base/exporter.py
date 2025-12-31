from abc import ABC, abstractmethod
from typing import Any

class ExporterBase(ABC):
    @abstractmethod
    def export(self, data: Any, destination: str, **kwargs) -> None:
        pass
