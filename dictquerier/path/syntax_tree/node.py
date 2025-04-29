from typing import Union, List, Optional

class ASTNode:
    """
    抽象语法树基类
    """
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
    def __init__(self, name: NameNode, args: List[ASTNode], line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(self.__class__.__name__, line, column)
        self.name: NameNode = name
        self.args: List[ASTNode] = args


class BinaryOpNode(ASTNode):
    """
    二元运算符节点
    """
    def __init__(self, left: ASTNode, op: str, right: ASTNode, line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(self.__class__.__name__, line, column)
        self.left: ASTNode = left
        self.op: str = op
        self.right: ASTNode = right


class AttributeNode(ASTNode):
    """
    属性节点
    """
    def __init__(self, obj: ASTNode, attr: str, line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(self.__class__.__name__, line, column)
        self.obj: ASTNode = obj
        self.attr: str = attr


class KeyNode(ASTNode):
    """
    字典键访问节点
    """
    def __init__(self, obj: ASTNode, key: str, line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(self.__class__.__name__, line, column)
        self.obj: ASTNode = obj
        self.key: str = key

class IndexNode(ASTNode):
    """
    索引节点
    """
    def __init__(self, obj: ASTNode, index: ASTNode, line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(self.__class__.__name__, line, column)
        self.obj: ASTNode = obj
        self.index: ASTNode = index

