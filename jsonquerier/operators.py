"""
操作符模块
"""
from enum import Enum

class Opreater(Enum):
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