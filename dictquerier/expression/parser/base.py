from abc import ABC, abstractmethod
from ast import List
from typing import Any, Optional, Union

from dictquerier.expression.base import BaseExpression
from dictquerier.operator.enum import Operator

class BaseParser(ABC):
    """
    表达式解析器基类，所有表达式解析器都必须继承自该类
    """
    
    @abstractmethod
    def parse(self, expression_str: str) -> BaseExpression:
        """解析表达式字符串为表达式对象"""
        pass
    
    @abstractmethod
    def can_parse(self, expression_str: str) -> bool:
        """判断是否可以解析该表达式"""
        pass

class ExpressionParserContext:
    """
    表达式解析上下文，用于存储解析过程中的状态和配置
    """
    
    def __init__(self):
        self.parsers: List[BaseParser] = []
        
    def register_parser(self, parser: BaseParser):
        """
        注册解析器
        """
        self.parsers.append(parser)
        
    def parse(self, expression_str: str) -> BaseExpression:
        """
        使用合适的解析器解析表达式
        """
        for parser in self.parsers:
            if parser.can_parse(expression_str):
                return parser.parse(expression_str)
        raise ValueError(f"无法解析表达式: {expression_str}")
