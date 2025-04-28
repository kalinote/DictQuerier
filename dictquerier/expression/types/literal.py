
from dictquerier.expression.base import BaseExpression


class LiteralExpression(BaseExpression):
    """
    字面量表达式
    """
    def __init__(self, value):
        super().__init__(value=value)

    def operate(self, data):
        return self.value

    def get_expression(self):
        return self.value
