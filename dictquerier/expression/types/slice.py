
from dictquerier.expression.base import BaseExpression
from dictquerier.operator.enum import Operator


class SliceExpression(BaseExpression):
    """
    切片表达式
    """
    def __init__(self, value: slice):
        super().__init__(value=value, operator=Operator.SLICE)

    def operate(self, data):
        return data[self.value]

    def get_expression(self):
        return f"{str(self.value.start) if self.value.start is not None else ''}:{str(self.value.stop) if self.value.stop is not None else ''}{f':{str(self.value.step)}' if self.value.step is not None and self.value.step != 1 else ''}"
