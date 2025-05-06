from typing import Dict, Union, List, Optional
from dictquerier.tokenizer.enum import Operator

class ASTNode:
    """
    抽象语法树基类
    """
    def accept(self, visitor):
        method_name = f'visit_{self.__class__.__name__}'
        method = getattr(visitor, method_name, visitor.generic_visit)
        return method(self)
    
    def __init__(self, type_: str, line: Optional[int] = None, column: Optional[int] = None) -> None:
        self.type: str = type_
        self.line: Optional[int] = line
        self.column: Optional[int] = column

    def __repr__(self) -> str:
        return f"{self.type}({self.__dict__})"

class NameNode(ASTNode):
    """
    标识符节点
    """
    def __init__(self, name: str, line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(self.__class__.__name__, line, column)
        self.name: str = name

class NumberNode(ASTNode):
    """
    数字节点
    """
    def __init__(self, value: str, line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(self.__class__.__name__, line, column)
        # 处理带负号的数字字符串
        self.value: Union[int, float] = float(value) if '.' in value or 'e' in value.lower() else int(value)
        
class StringNode(ASTNode):
    """
    字符串节点
    """
    def __init__(self, value: str, line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(self.__class__.__name__, line, column)
        self.value: str = value
        


class VarRefNode(ASTNode):
    """
    变量引用节点
    """
    def __init__(self, name: NameNode, line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(self.__class__.__name__, line, column)
        self.name: NameNode = name

class ScriptCallNode(ASTNode):
    """
    脚本调用节点
    """
    def __init__(self, module: NameNode, name: NameNode, args: List[ASTNode], kwargs: Dict[str, ASTNode], line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(self.__class__.__name__, line, column)
        self.module: List[NameNode] = module
        self.name: NameNode = name
        self.args: List[ASTNode] = args
        self.kwargs: Dict[str, ASTNode] = kwargs


class BinaryOpNode(ASTNode):
    """
    二元运算符节点
    """
    def __init__(self, left: ASTNode, op: Union[str, Operator], right: ASTNode, line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(self.__class__.__name__, line, column)
        self.left: ASTNode = left
        # 确保op是Operator枚举实例
        self.op: Operator = op if isinstance(op, Operator) else self._str_to_operator(op)
        self.right: ASTNode = right
    
    @staticmethod
    def _str_to_operator(op_str: str) -> Operator:
        """将字符串转换为Operator枚举"""
        for op in Operator:
            if op.value == op_str:
                return op
        raise ValueError(f"不支持的操作符: {op_str}")

class KeyNode(ASTNode):
    """
    字典键访问节点
    """
    def __init__(self, obj: ASTNode, key: str, is_wildcard: bool = False, line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(self.__class__.__name__, line, column)
        self.obj: ASTNode = obj
        self.key: str = key
        self.is_wildcard: bool = is_wildcard

class IndexNode(ASTNode):
    """
    索引节点
    """
    def __init__(self, obj: ASTNode, index: ASTNode, line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(self.__class__.__name__, line, column)
        self.obj: ASTNode = obj
        self.index: ASTNode = index

class SliceNode(ASTNode):
    """
    基础切片节点
    """
    def __init__(self, obj: ASTNode, start: ASTNode, end: ASTNode, step: ASTNode, line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(self.__class__.__name__, line, column)
        self.obj: ASTNode = obj
        self.start: ASTNode = start
        self.end: ASTNode = end
        self.step: ASTNode = step
