from abc import ABC, abstractmethod

from jsonquerier.operator.enum import Operator
from jsonquerier.operator.register import OperatorRegister


class BaseExpression(ABC):
    """
    表达式基类，所有表达式类都必须继承自该类
    """
    def __init__(self, key = None, value = None, left: "BaseExpression" = None, right: "BaseExpression" = None, operator: Operator = None):
        self.key = key
        self.value = value
        self.left = left
        self.right = right
        self.operator = operator
        self.handler = OperatorRegister.get_handler(self.operator)
    
    @abstractmethod
    def operate(self, data):
        pass
    
    @abstractmethod
    def get_expression(self):
        pass
    