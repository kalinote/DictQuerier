from jsonquerier.expression.base import BaseExpression
from jsonquerier.operator.base import OperatorHandlerBase
from jsonquerier.operator.enum import Operator
from jsonquerier.operator.register import OperatorRegister


class LogicalOperatorHandler(OperatorHandlerBase):
    """
    逻辑运算符处理类
    """
    @staticmethod
    def execute(expression: BaseExpression, data) -> bool:
        raise NotImplementedError("逻辑运算符处理类必须实现execute方法")


class AndOperatorHandler(LogicalOperatorHandler):
    """
    与运算符处理类
    """
    @staticmethod
    def execute(expression: BaseExpression, data) -> bool:
        return expression.left.operate(data) and expression.right.operate(data)


class OrOperatorHandler(LogicalOperatorHandler):
    """
    或运算符处理类
    """
    @staticmethod
    def execute(expression: BaseExpression, data) -> bool:
        return expression.left.operate(data) or expression.right.operate(data)


OperatorRegister.register(Operator.LOGICAL_AND, AndOperatorHandler)
OperatorRegister.register(Operator.LOGICAL_OR, OrOperatorHandler)

