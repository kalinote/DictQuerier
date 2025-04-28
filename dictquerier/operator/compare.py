from dictquerier.operator.base import OperatorHandlerBase
from dictquerier.operator.enum import Operator, OperatorType
from dictquerier.operator.register import OperatorRegister


class CompareOperatorHandler(OperatorHandlerBase):
    """
    比较运算符处理类
    """
    @staticmethod
    def compare(left, right) -> bool:
        raise NotImplementedError("比较运算符处理类必须实现compare方法")
    
    @staticmethod
    def execute(expression, data) -> list:
        raise NotImplementedError("比较运算符暂不支持execute方法")
    
    @classmethod
    def get_operator_type(cls):
        """
        获取运算符类型
        """
        return OperatorType.COMPARE
    
    @classmethod
    def is_compare_operator(cls):
        return True


class EqualOperatorHandler(CompareOperatorHandler):
    """
    等于运算符处理类
    """
    @staticmethod
    def compare(left, right) -> bool:
        return left == right


class NotEqualOperatorHandler(CompareOperatorHandler):
    """
    不等于运算符处理类
    """
    @staticmethod
    def compare(left, right) -> bool:
        return left != right


class LessThanOperatorHandler(CompareOperatorHandler):
    """
    小于运算符处理类
    """
    @staticmethod
    def compare(left, right) -> bool:
        return left < right


class LessThanOrEqualOperatorHandler(CompareOperatorHandler):
    """
    小于等于运算符处理类
    """
    @staticmethod
    def compare(left, right) -> bool:
        return left <= right


class GreaterThanOperatorHandler(CompareOperatorHandler):
    """
    大于运算符处理类
    """
    @staticmethod
    def compare(left, right) -> bool:
        return left > right


class GreaterThanOrEqualOperatorHandler(CompareOperatorHandler):
    """
    大于等于运算符处理类
    """
    @staticmethod
    def compare(left, right) -> bool:
        return left >= right


OperatorRegister.register(Operator.EQUAL, EqualOperatorHandler)
OperatorRegister.register(Operator.NOT_EQUAL, NotEqualOperatorHandler)
OperatorRegister.register(Operator.LESS_THAN, LessThanOperatorHandler)
OperatorRegister.register(Operator.LESS_EQUAL, LessThanOrEqualOperatorHandler)
OperatorRegister.register(Operator.GREATER_THAN, GreaterThanOperatorHandler)
OperatorRegister.register(Operator.GREATER_EQUAL, GreaterThanOrEqualOperatorHandler)

