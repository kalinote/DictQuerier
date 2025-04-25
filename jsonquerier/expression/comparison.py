
from jsonquerier.expression.base import BaseExpression
from jsonquerier.operator.enum import Operator


class ComparisonExpression(BaseExpression):
    """
    比较表达式
    """
    def __init__(self, key, value, operator: Operator):
        super().__init__(key = key, value = value, operator = operator)
        
    def operate(self, data):
        from jsonquerier.core import query_json
        result_list = []
        for item in data:
            result = query_json(item, self.key, no_path_exception=True)
            if self.handler.compare(result, self.value):
                result_list.append(item)
        return result_list

    def get_expression(self):
        value = f'"{self.value}"' if isinstance(self.value, str) else self.value
        return f'"{self.key}" {self.operator.value} {value}'
