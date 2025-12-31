from abc import ABC, abstractmethod
from typing import Any

class LoaderBase(ABC):
    @abstractmethod
    def load(self, **kwargs) -> Any:
        pass
