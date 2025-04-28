import ast
import random
import re
import string

from dictquerier.expression.base import BaseExpression
from dictquerier.expression.types.comparison import ComparisonExpression
from dictquerier.expression.types.literal import LiteralExpression
from dictquerier.expression.types.logical import LogicalExpression
from dictquerier.expression.types.slice import SliceExpression
from dictquerier.operator.enum import Operator

class ExpressionParser:
    """
    表达式解析器
    """
    
    @staticmethod
    def parse(expression: str) -> BaseExpression:
        expression = expression.strip()
        
        # 这个判断有问题，比如形如 '( "id"==2 && "name"=="value4" ) || ( "id"==2 && "sub_id" == "A" )' 这种表达式，处理后会变成 "id"==2 && "name"=="value4" ) || ( "id"==2 && "sub_id" == "A"
        # if expression.startswith("(") and expression.endswith(")"):
            # return ExpressionParser.parse(expression[1:-1])
        if expression.startswith("(") and expression.endswith(")"):
            depth = 0
            for i, char in enumerate(expression):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                if depth == 0 and i != len(expression) - 1:
                    break
            else:
                return ExpressionParser.parse(expression[1:-1])

        # 处理逻辑表达式
        index, operator = ExpressionParser._find_outer_operator(expression)
        if index != -1 and operator != None:
            return LogicalExpression(
                left=ExpressionParser.parse(expression[:index].strip()),
                right=ExpressionParser.parse(expression[index+len(operator.value):].strip()),
                operator=operator
            )

        # TODO 首先判断表达式中是否有脚本运算
        script_calls = re.findall(r'@[a-zA-Z_][a-zA-Z0-9_]*\(.*\)', expression)
        if script_calls:
            raise NotImplementedError(f"脚本运算暂未实现: {script_calls}")
        for call in script_calls:
            script = ast.parse(call, mode='eval')
            if not isinstance(script, ast.Call):
                raise SyntaxError(f"表达式符合脚本格式 <{call}>，但解析错误: {expression}")

        # 处理基本比较表达式
        # match = re.match(r'^("[^"]+"|\'[^\']+\')\s*(==|!=|<=|>=|<|>)\s*(\d+|"[^"]+"|\'[^\']+\'|true|True|False|false|None|null)$', expression)
        match = re.match(r'^(.+)\s*(==|!=|<=|>=|<|>)\s*(.+)$', expression)
        if match:
            key, operator_str, value = match.groups()
            key = key.strip().strip("'").strip('"')
            value = value.strip().strip("'").strip('"')
            if value.isdigit():
                value = int(value)
            elif value.startswith('"') or value.startswith("'"):
                value = value[1:-1]  # 去除引号
                
            # 将字符串运算符转换为枚举
            operator = ExpressionParser._get_operator(operator_str)
            return ComparisonExpression(key=key, value=value, operator=operator)
        
        # 简单数字索引
        if expression.isdigit():
            return LiteralExpression(int(expression))
        
        # 双引号文本字符串
        if re.match(r'^"[^"]*"$', expression):
            return LiteralExpression(expression.strip('"'))
        
        # 单引号文本字符串
        if re.match(r"^'[^']*'$", expression):
            return LiteralExpression(expression.strip("'"))
        
        # 简单文本
        if re.match(r'^\w+$', expression):
            return LiteralExpression(expression)
        
        # 单个通配符
        if expression == "*":
            return LiteralExpression("*")

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
                
                return SliceExpression(slice(start, end, step))
            
            if isinstance(slice_node, ast.Tuple):
                # TODO 实现扩展索引(类似list[1,2:3]这种)
                raise NotImplementedError("扩展索引暂未实现")
        
        raise SyntaxError(f"无效表达式: {expression}")

    @staticmethod
    def _find_outer_operator(expression: str) -> tuple[int, Operator]:
        """
        查找表达式中的外层运算符
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
                for complex_op in [Operator.LOGICAL_AND, Operator.LOGICAL_OR]:
                    if expression[i:i+len(complex_op.value)] == complex_op.value:
                        last_operator_index = i
                        operator = complex_op
                        break
            escaped = False
        return last_operator_index, operator
                

    @staticmethod
    def _get_operator(operator_str: str) -> Operator:
        """根据操作符字符串获取对应的操作符枚举"""
        for op_enum in Operator:
            if op_enum.value == operator_str:
                return op_enum
        raise SyntaxError(f"未知的运算符: {operator_str}")
