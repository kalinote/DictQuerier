from .base import BaseNode

class WildcardNode(BaseNode):
    def get_value(self):
        return "*"

    def get_path(self) -> str:
        return "[*]"
