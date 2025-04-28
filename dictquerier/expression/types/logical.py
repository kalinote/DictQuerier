from dictquerier.expression.base import BaseExpression
from dictquerier.operator.enum import Operator


class LogicalExpression(BaseExpression):
    """
    逻辑表达式
    """
    def __init__(self, left: BaseExpression, right: BaseExpression, operator: Operator):
        super().__init__(left=left, right=right, operator=operator)

    def operate(self, data):
        return self.handler.operate(expression=self, data=data)

    def get_expression(self):
        return f"({self.left.get_expression()} {self.operator.value} {self.right.get_expression()})"
