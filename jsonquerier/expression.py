"""
表达式解析模块
"""
import ast
import random
import re
import string
from typing import Any, Union, List, Dict

from .operators import Opreater

class Expression:
    """
    表达式类，用于解析和执行查询表达式
    """
    operator_funcs = {
        Opreater.EQUAL: lambda x, y: x == y,
        Opreater.LESS_THAN: lambda x, y: x < y,
        Opreater.GREATER_THAN: lambda x, y: x > y,
        Opreater.LESS_EQUAL: lambda x, y: x <= y,
        Opreater.GREATER_EQUAL: lambda x, y: x >= y,
        Opreater.NOT_EQUAL: lambda x, y: x != y,
    }
    complex_operator_funcs = {
        Opreater.LOGICAL_AND: lambda x, y: x.right.operate(x.left.operate(y)),
        Opreater.LOGICAL_OR: lambda x, y: x.left.operate(y) + x.right.operate(y),
    }
    
    def __init__(self, key=None, operator=None, value=None, left=None, right=None):
        self.key = key
        self.operator = operator
        self.value = value
        self.left: Expression = left
        self.right: Expression = right
        
    def __repr__(self):
        if self.key:
            return f'Expression({self.key} {self.operator} {self.value})'
        elif self.value is not None:
            return f'Expression(value={self.value})'
        else:
            return f'({self.left} {self.operator} {self.right})'

    def get_expression(self):
        if self.key:
            value = f'"{self.value}"' if isinstance(self.value, str) else self.value
            return f'"{self.key}" {self.operator} {value}'
        elif self.value is not None:
            return self.value
        else:
            return f'({self.left.get_expression()} {self.operator} {self.right.get_expression()})'

    def operate(self, data):
        # 基本运算符
        if self.operator in self.complex_operator_funcs:
            return self.complex_operator_funcs[self.operator](self, data)
        
        # 逻辑操作符
        if self.operator in self.operator_funcs:
            itempack_list = []
            for item_pack in data:
                from .core import query_json
                result = query_json(item_pack, self.key, no_path_exception=True)
                
                if self.operator_funcs[self.operator](result, self.value):
                    itempack_list.append(item_pack)
            return itempack_list
        
        # 切片索引
        if self.operator == Opreater.SLICE:
            return data[self.value]
        
        else:
            raise SyntaxError(f"不支持的运算符: {self.operator}")

    @staticmethod
    def parse(expression: str) -> "Expression":
        expression = expression.strip()
        if expression.startswith("(") and expression.endswith(")"):
            return Expression.parse(expression[1:-1])

        index, operator = Expression.find_outer_operator(expression)
        if index != -1:
            return Expression(left=Expression.parse(expression[:index].strip()),
                              operator=operator,
                              right=Expression.parse(expression[index+len(operator.value):].strip()))

        # 处理比较表达式
        match = re.match(r'("[^"]+"|\'[^\']+\')\s*(==|!=|<=|>=|<|>)\s*(\d+|"[^"]+"|\'[^\']+\'|true|True|False|false|None|null)$', expression)
        if match:
            key, operator_str, value = match.groups()
            key = key.strip("'").strip('"')
            value = value.strip("'").strip('"')
            if value.isdigit():
                value = int(value)
            elif value.startswith('"') or value.startswith("'"):
                value = value[1:-1]  # 去除引号
            
            # 将字符串运算符转换为枚举
            operator = None
            for op_enum in Opreater:
                if op_enum.value == operator_str:
                    operator = op_enum
                    break
            
            if operator is None:
                raise SyntaxError(f"未知的运算符: {operator_str}")
                
            return Expression(key=key, operator=operator, value=value)

        # 处理简单文本或数字索引
        # 简单数字索引
        if expression.isdigit():
            return Expression(value=int(expression))
        
        # 双引号文本字符串
        if re.match(r'^"[^"]*"$', expression):
            return Expression(value=expression.strip('"'))
        
        # 单引号文本字符串
        if re.match(r"^'[^']*'$", expression):
            return Expression(value=expression.strip("'"))
        
        # 简单文本
        if re.match(r'^\w+$', expression):
            return Expression(value=expression)
        
        # 单个通配符
        if expression == "*":
            return Expression(value="*")

        # 处理复杂切片索引
        try:
            tree = ast.parse(f"__slice_check_{''.join(random.choices(string.ascii_letters + string.digits, k=8))}__[{expression}]", mode='eval')
        except Exception as e:
            # 这里是最后一步解析，如果到这一步都解析失败，说明是无效表达式
            raise SyntaxError(f"无效表达式: {expression}")
        if isinstance(tree, ast.Expression) or isinstance(tree.body, ast.Subscript):
            slice_node = tree.body.slice
            if isinstance(slice_node, ast.Slice):
                start = ast.literal_eval(slice_node.lower) if slice_node.lower else None
                end = ast.literal_eval(slice_node.upper) if slice_node.upper else None
                step = ast.literal_eval(slice_node.step) if slice_node.step else None
                
                if not (isinstance(start, int) or start is None) or not (isinstance(end, int) or end is None) or not (isinstance(step, int) or step is None):
                    raise ValueError(f"切片索引必须是整数或None: [{expression}]")
                
                if step == 0:
                    raise ValueError(f"切片步长不能为0: [{expression}]")
                
                return Expression(operator=Opreater.SLICE, value=slice(start, end, step))
            
            if isinstance(slice_node, ast.Tuple):
                # TODO 实现扩展索引(类似list[1,2:3]这种)
                raise NotImplementedError("扩展索引暂未实现")

        
        raise SyntaxError(f"无效表达式: {expression}")

    @staticmethod
    def find_outer_operator(expression):
        """查找表达式中的外层运算符

        Args:
            expression (str): 表达式字符串

        Returns:
            tuple: 包含外层运算符的索引和运算符，如果索引为-1，则表示没有找到外层运算符
        """
        depth = 0
        last_operator_index = -1
        operator = None
        escaped = False
        for i, char in enumerate(expression):
            if char == '\\' and not escaped:
                escaped = True
                continue
            if char == '(' and not escaped:
                depth += 1
            elif char == ')' and not escaped:
                depth -= 1
            elif depth == 0 and i + 1 < len(expression):
                # 检查是否是复杂运算符(&&, ||)
                for complex_op in [Opreater.LOGICAL_AND, Opreater.LOGICAL_OR]:
                    if expression[i:i+len(complex_op.value)] == complex_op.value:
                        last_operator_index = i
                        operator = complex_op
                        break
            escaped = False
        return last_operator_index, operator

def parse_path(path: str) -> List[Union[str, int]]:
    """
    解析JSON路径表达式

    Args:
        path (str): JSON路径表达式

    Returns:
        List[Union[str, int]]: 解析后的路径元素列表
    """
    elements = []
    buffer = ''
    escaped = False
    i = 0
    
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
    
    while i < len(path):
        if escaped:
            buffer += path[i]
            escaped = False
        elif path[i] == '\\':
            escaped = True
        elif path[i] == '.':
            if buffer:
                elements.append(_convert_buffer(buffer))
                buffer = ''
        elif path[i] == '[':
            if buffer:
                elements.append(_convert_buffer(buffer))
                buffer = ''
            # 检查是否是简单的字符串键访问（带引号的键名）
            if i + 1 < len(path) and (path[i+1] == '"' or path[i+1] == "'"):
                quote_char = path[i+1]
                j = i + 2
                key = ''
                while j < len(path) and path[j] != quote_char:
                    if path[j] == '\\' and j + 1 < len(path):
                        j += 1
                        key += path[j]
                    else:
                        key += path[j]
                    j += 1
                
                if j < len(path) and path[j] == quote_char and j + 1 < len(path) and path[j+1] == ']':
                    elements.append(_convert_buffer(key))
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
                    
                    expression = Expression.parse(inside_syntax)
                    
                    if not expression.operator:
                        # 索引key或下标
                        elements.append(expression.value)
                    else:
                        # 表达式
                        elements.append(expression)
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
                
                expression = Expression.parse(inside_syntax)
                
                if not expression.operator:
                    # 索引key、下标、切片
                    elements.append(expression.value)
                else:
                    # 表达式
                    elements.append(expression)
                buffer = ''
                i += len(inside_syntax) + 1  # 包含最后的']'
        else:
            buffer += path[i]
        i += 1
    if buffer:  # 确保最后一个元素被添加
        elements.append(_convert_buffer(buffer))
    return elements

def elements2path(elements: list):
    """
    将路径元素列表转换回路径字符串

    Args:
        elements (list): 路径元素列表

    Returns:
        str: 路径字符串
    """
    path = ""
    for idx, element in enumerate(elements):
        if isinstance(element, str):
            if element == "*":
                # TODO 暂时这么写，因为目前通配符还没有其他作用
                path = path.rstrip('.') + "[*]"
            else:
                path += element
        elif isinstance(element, int):
            path = path.rstrip('.') + f"[{element}]"
        elif isinstance(element, Expression):
            path = path.rstrip('.') + f"[{element.get_expression()}]"
        else:
            path += str(element)
        if idx < len(elements)-1:
            path += "."
    return path 