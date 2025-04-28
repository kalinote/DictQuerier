from abc import ABC, abstractmethod
from typing import Any

from dictquerier.expression.base import BaseExpression
from dictquerier.expression.types.comparison import ComparisonExpression
from dictquerier.expression.types.logical import LogicalExpression
from dictquerier.expression.types.literal import LiteralExpression
from dictquerier.expression.types.slice import SliceExpression

class ExpressionVisitor(ABC):
    @abstractmethod
    def visit(self, expression: BaseExpression) -> Any:
        pass
    
    
