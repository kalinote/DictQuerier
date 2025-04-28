from abc import ABC, abstractmethod

from dictquerier.operator.enum import OperatorType


class OperatorHandlerBase(ABC):
    """
    运算符处理基类
    """
    @staticmethod
    @abstractmethod
    def execute(expression, data) -> list:
        pass
    
    @staticmethod
    @abstractmethod
    def compare(left, right) -> bool:
        pass
    
    @classmethod
    def operate(cls, expression=None, data=None, left=None, right=None):
        """
        统一的操作入口，根据运算符类型自动选择正确的方法
        
        参数:
            expression: 表达式对象，用于逻辑运算等需要表达式的运算
            data: 要处理的数据，用于逻辑运算等
            left: 左操作数，用于比较运算等
            right: 右操作数，用于比较运算等
            
        返回:
            运算结果
        """
        # 通过子类实现的类方法获取运算符类型
        if hasattr(cls, 'get_operator_type'):
            operator_type = cls.get_operator_type()
            
            if operator_type == OperatorType.COMPARE:
                return cls.compare(left, right)
            elif operator_type == OperatorType.LOGICAL:
                return cls.execute(expression, data)
            else:
                raise NotImplementedError(f"未实现的运算符类型: {operator_type}")
        else:
            raise NotImplementedError("运算符处理类必须实现get_operator_type方法")

    @classmethod
    def get_operator_type(cls):
        """
        获取运算符类型
        子类必须实现该方法，返回运算符类型的枚举值
        例如: OperatorType.COMPARE, OperatorType.LOGICAL 等
        """
        raise NotImplementedError("子类必须实现get_operator_type方法")

    @classmethod
    def is_compare_operator(cls):
        """
        判断是否为比较运算符
        默认返回False
        """
        return False
