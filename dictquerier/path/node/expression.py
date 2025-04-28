from typing import Any
from dictquerier.expression.base import BaseExpression
from .base import BaseNode

class ExpressionNode(BaseNode):
    """封装表达式类型的路径节点"""
    def __init__(self, expression: BaseExpression):
        self.expression = expression
        
    def get_value(self) -> Any:
        # 返回底层表达式对象
        return self.expression
    
    def get_path(self) -> str:
        return f"[{self.expression.get_expression()}]"
