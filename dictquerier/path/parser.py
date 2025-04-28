import ast
from typing import List, Union

from dictquerier.expression.base import BaseExpression
from dictquerier.expression.types.literal import LiteralExpression
from dictquerier.expression.parser.parser import ExpressionParser

from dictquerier.path.node.base import BaseNode
from dictquerier.path.node.expression import ExpressionNode
from dictquerier.path.node.key import KeyNode
from dictquerier.path.node.wildcard import WildcardNode
from dictquerier.path.node.index import IndexNode

class PathParser:
    """
    路径解析器
    """
    
    @staticmethod
    def parse(path: str) -> List[BaseNode]:
        nodes = []
        buffer = ''
        escaped = False
        i = 0
        
        while i < len(path):
            if escaped:
                buffer += path[i]
                escaped = False
            elif path[i] == '\\':
                escaped = True
            elif path[i] == '.':
                if buffer:
                    nodes.append(PathParser._to_node(PathParser._convert_buffer(buffer)))
                    buffer = ''
            elif path[i] == '[':
                if buffer:
                    nodes.append(PathParser._to_node(PathParser._convert_buffer(buffer)))
                    buffer = ''
                # 检查是否是简单的字符串键访问（带引号的键名）
                if i + 1 < len(path) and (path[i+1] == '"' or path[i+1] == "'"):
                    quote_char = path[i+1]
                    j = i + 2
                    
                    # 带上引号方便在格式转换时进行判断
                    key = quote_char
                    while j < len(path) and path[j] != quote_char:
                        if path[j] == '\\' and j + 1 < len(path):
                            j += 1
                            key += path[j]
                        else:
                            key += path[j]
                        j += 1
                    key += quote_char
                    
                    if j < len(path) and path[j] == quote_char and j + 1 < len(path) and path[j+1] == ']':
                        nodes.append(PathParser._to_node(PathParser._convert_buffer(key)))
                        i = j + 1  # 跳到 ']' 之后
                    else:
                        # 如果不是简单的键访问，则按表达式处理
                        j = i + 1
                        inside_syntax = ''
                        # 先将子语句全部提取出
                        while j < len(path) and path[j] != ']':
                            inside_syntax += path[j]
                            j += 1
                        if j == len(path) and path[j-1] != ']':
                            raise SyntaxError("未关闭的方括号")
                        
                        expression = ExpressionParser.parse(inside_syntax)
                        nodes.append(PathParser._to_node(expression.value if isinstance(expression, LiteralExpression) else expression))
                        buffer = ''
                        i += len(inside_syntax) + 1  # 包含最后的']'
                else:
                    # 按表达式处理
                    j = i + 1
                    inside_syntax = ''
                    while j < len(path) and path[j] != ']':
                        inside_syntax += path[j]
                        j += 1
                    if j == len(path) and path[j-1] != ']':
                        raise SyntaxError("未关闭的方括号")
                    
                    expression = ExpressionParser.parse(inside_syntax)
                    nodes.append(PathParser._to_node(expression.value if isinstance(expression, LiteralExpression) else expression))
                    buffer = ''
                    i += len(inside_syntax) + 1  # 包含最后的']'
            else:
                buffer += path[i]
            i += 1
        if buffer:  # 确保最后一个元素被添加
            nodes.append(PathParser._to_node(PathParser._convert_buffer(buffer)))
        return nodes

    @staticmethod
    def nodes2path(nodes: List[BaseNode]) -> str:
        """将路径元素列表转换为路径字符串"""
        path = ""
        for idx, node in enumerate(nodes):
            path += node.get_path()
        return path 

    @staticmethod
    def _to_node(val):
        if isinstance(val, BaseExpression):
            return ExpressionNode(val)
        if isinstance(val, int):
            return IndexNode(val)
        if isinstance(val, str) and val == "*":
            return WildcardNode()
        # 其它情况当作 key
        return KeyNode(val)

    @staticmethod
    def _convert_buffer(buf: str) -> Union[str, int, float, bool, None]:
        """通用类型转换"""
        if (buf.startswith("'") and buf.endswith("'")) or (buf.startswith('"') and buf.endswith('"')):
            return buf[1:-1]
        if buf.isdigit():
            # 处理整数
            return int(buf)
        try:
            # 处理浮点
            return float(buf)
        except ValueError:
            pass
        if buf.lower() in ('true', 'false'):
            # 处理布尔值
            return buf.lower() == 'true'
        if buf.lower() in ('null', 'none'):
            # 处理None
            return None
        if buf.startswith('(') and buf.endswith(')'):
            # 处理元组
            try:
                return ast.literal_eval(buf)
            except:
                pass
        return buf  # 默认返回字符串
