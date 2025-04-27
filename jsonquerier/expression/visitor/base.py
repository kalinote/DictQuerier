from abc import ABC, abstractmethod
from typing import Any

from jsonquerier.expression.base import BaseExpression
from jsonquerier.expression.types.comparison import ComparisonExpression
from jsonquerier.expression.types.logical import LogicalExpression
from jsonquerier.expression.types.literal import LiteralExpression
from jsonquerier.expression.types.slice import SliceExpression

class ExpressionVisitor(ABC):
    @abstractmethod
    def visit(self, expression: BaseExpression) -> Any:
        pass
    
    
