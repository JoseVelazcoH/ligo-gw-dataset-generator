from abc import ABC, abstractmethod
from typing import Any

class TransformerBase(ABC):
    @abstractmethod
    def transform(self, data: Any, **kwargs) -> Any:
        pass
