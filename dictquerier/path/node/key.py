from typing import Any
from dictquerier.path.node.base import BaseNode

class KeyNode(BaseNode):
    """字典键

    可以是任意可hash的数据类型(可以作为字典键的类型)
    """
    def __init__(self, key: Any):
        self.key = key
        
    def get_value(self) -> Any:
        return self.key
    
    def get_path(self) -> str:
        return f".{self.key}"
