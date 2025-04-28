
from dictquerier.operator.base import OperatorHandlerBase
from dictquerier.operator.enum import Operator


class OperatorRegister:
    """
    运算符注册类，管理所有操作符处理器
    """
    _handlers = {}

    @classmethod
    def register(cls, operator: Operator, handler: OperatorHandlerBase):
        """注册操作符处理器"""
        cls._handlers[operator] = handler
        
    @classmethod
    def get_handler(cls, operator: Operator) -> OperatorHandlerBase:
        """获取操作符对应的处理器"""
        return cls._handlers.get(operator)
