from jsonquerier.expression.base import BaseExpression
from jsonquerier.operator.base import OperatorHandlerBase
from jsonquerier.operator.enum import Operator
from jsonquerier.operator.register import OperatorRegister


class LogicalOperatorHandler(OperatorHandlerBase):
    """
    逻辑运算符处理类
    """
    @staticmethod
    def execute(expression: BaseExpression, data) -> list:
        raise NotImplementedError("逻辑运算符处理类必须实现execute方法")
    
    @staticmethod
    def compare(left, right) -> bool:
        return NotImplementedError("逻辑运算符暂不支持compare方法")


class AndOperatorHandler(LogicalOperatorHandler):
    """
    与运算符处理类
    """
    @staticmethod
    def execute(expression: BaseExpression, data) -> list:
        return expression.right.operate(expression.left.operate(data))


class OrOperatorHandler(LogicalOperatorHandler):
    """
    或运算符处理类
    """
    @staticmethod
    def execute(expression: BaseExpression, data) -> list:
        return list(set(expression.left.operate(data) + expression.right.operate(data)))


OperatorRegister.register(Operator.LOGICAL_AND, AndOperatorHandler)
OperatorRegister.register(Operator.LOGICAL_OR, OrOperatorHandler)

