from abc import ABC, abstractmethod
from typing import Any

class BaseNode(ABC):
    @abstractmethod
    def get_value(self) -> Any:
        pass
    
    @abstractmethod
    def get_path(self) -> str:
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.get_value()!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, BaseNode) and type(self) is type(other) and self.get_value() == other.get_value()
    