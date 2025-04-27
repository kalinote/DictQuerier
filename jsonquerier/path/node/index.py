from typing import Any
from jsonquerier.path.node.base import BaseNode

class IndexNode(BaseNode):
    def __init__(self, index: int):
        self.index = index
        
    def get_value(self) -> Any:
        return self.index
    
    def get_path(self) -> str:
        return f"[{self.index}]"