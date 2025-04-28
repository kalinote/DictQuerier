"""
操作符模块
"""
from enum import Enum

class Operator(Enum):
    """
    Operator 枚举类
    用于定义支持的操作符类型，便于后续表达式解析和判断。
    """
    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    LOGICAL_AND = "&&"
    LOGICAL_OR = "||"
    SLICE = "slice"

    def __str__(self):
        return self.value 


class OperatorType(Enum):
    """
    OperatorType 枚举类
    用于定义操作符的类型，便于分派不同的处理方法。
    """
    COMPARE = "compare"
    LOGICAL = "logical"
    ARITHMETIC = "arithmetic"
    
    def __str__(self):
        return self.value 