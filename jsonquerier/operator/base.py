from abc import ABC, abstractmethod


class OperatorHandlerBase(ABC):
    """
    运算符处理基类
    """
    @staticmethod
    @abstractmethod
    def execute(expression, data) -> bool:
        pass
    
    @staticmethod
    @abstractmethod
    def compare(left, right) -> bool:
        pass
