from dictquerier.expression.base import BaseExpression
from dictquerier.operator.base import OperatorHandlerBase
from dictquerier.operator.enum import Operator, OperatorType
from dictquerier.operator.register import OperatorRegister


class LogicalOperatorHandler(OperatorHandlerBase):
    """
    逻辑运算符处理类
    """
    @staticmethod
    def execute(expression: BaseExpression, data) -> list:
        raise NotImplementedError("逻辑运算符处理类必须实现execute方法")
    
    @staticmethod
    def compare(left, right) -> bool:
        raise NotImplementedError("逻辑运算符暂不支持compare方法")
    
    @classmethod
    def get_operator_type(cls):
        """
        获取运算符类型
        """
        return OperatorType.LOGICAL


class AndOperatorHandler(LogicalOperatorHandler):
    """
    与运算符处理类
    """
    @staticmethod
    def execute(expression: BaseExpression, data) -> list:
        left_result = expression.left.operate(data)
        if not left_result:
            return []
        return expression.right.operate(left_result)


class OrOperatorHandler(LogicalOperatorHandler):
    """
    或运算符处理类
    """
    @staticmethod
    def execute(expression: BaseExpression, data) -> list:
        left_result = expression.left.operate(data)
        right_result = expression.right.operate(data)
        result = []
        for item in left_result + right_result:
            if not any(item == existed for existed in result):
                result.append(item)
        return result


OperatorRegister.register(Operator.LOGICAL_AND, AndOperatorHandler)
OperatorRegister.register(Operator.LOGICAL_OR, OrOperatorHandler)

