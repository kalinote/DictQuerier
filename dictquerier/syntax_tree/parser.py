from typing import List, Optional, Iterator
from dictquerier.tokenizer.token import Token
from dictquerier.tokenizer.enum import TokenType, Operator
from dictquerier.syntax_tree.node import (
    ASTNode, NameNode, NumberNode, StringNode, VarRefNode,
    ScriptCallNode, BinaryOpNode, AttributeNode, IndexNode, KeyNode, SliceNode
)


class Parser:
    """
    递归下降解析器，将Token序列解析为抽象语法树
    """
    def __init__(self, tokens: Iterator[Token]):
        self.tokens = [token for token in tokens if token.type != TokenType.WHITESPACE]  # 过滤掉所有空白符
        self.current = 0
        self.current_token = self.tokens[0] if self.tokens else None

    def parse(self) -> ASTNode:
        """
        解析入口，解析完整表达式并返回AST根节点
        """
        if not self.tokens:
            raise SyntaxError("没有可解析的令牌")
        
        # 常规解析
        result = self.expr()
        
        # 确保所有令牌都已解析（除了END）
        if self.current_token and self.current_token.type != TokenType.END:
            self.error(f"解析结束后仍有未处理的令牌: {self.current_token}")
            
        return result

    def error(self, message: str):
        """抛出语法错误异常"""
        line = self.current_token.line if self.current_token else "未知"
        column = self.current_token.column if self.current_token else "未知"
        raise SyntaxError(f"{message}，在行 {line} 列 {column}")

    def advance(self):
        """前进到下一个令牌"""
        self.current += 1
        if self.current < len(self.tokens):
            self.current_token = self.tokens[self.current]
        else:
            self.current_token = None

    def peek(self, offset: int = 1) -> Optional[Token]:
        """预览后面的令牌，不消耗当前令牌"""
        pos = self.current + offset
        if 0 <= pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def match(self, *types: TokenType) -> bool:
        """检查当前令牌是否匹配指定类型之一"""
        if self.current_token and self.current_token.type in types:
            self.advance()
            return True
        return False

    def expect(self, *types: TokenType) -> Token:
        """期望当前令牌是指定类型之一，否则报错"""
        if self.current_token and self.current_token.type in types:
            token = self.current_token
            self.advance()
            return token
        
        expected = " 或 ".join(t.literal for t in types)
        got = self.current_token.type.literal if self.current_token else "EOF"
        self.error(f"期望 {expected}，但得到了 {got}")

    # 表达式解析的各个级别，按优先级从低到高排列

    def expr(self) -> ASTNode:
        """解析逻辑表达式 (||, &&)"""
        left = self.comparison()
        
        while (self.current_token and self.current_token.type == TokenType.OP and 
               self.current_token.value in (Operator.LOGICAL_OR.value, Operator.LOGICAL_AND.value)):
            # 将操作符字符串转换为Operator枚举
            op_value = self.current_token.value
            op = Operator.LOGICAL_OR if op_value == Operator.LOGICAL_OR.value else Operator.LOGICAL_AND
            line, column = self.current_token.line, self.current_token.column
            self.advance()
            right = self.comparison()
            left = BinaryOpNode(left, op, right, line, column)
            
        return left

    def comparison(self) -> ASTNode:
        """解析比较表达式 (>, <, >=, <=, ==, !=)"""
        left = self.addition()
        
        while (self.current_token and self.current_token.type == TokenType.OP and 
               self.current_token.value in (
                   Operator.GREATER_THAN.value, 
                   Operator.LESS_THAN.value, 
                   Operator.GREATER_EQUAL.value, 
                   Operator.LESS_EQUAL.value, 
                   Operator.EQUAL.value, 
                   Operator.NOT_EQUAL.value
               )):
            # 将操作符字符串转换为Operator枚举
            op_value = self.current_token.value
            op = next(op for op in Operator if op.value == op_value)
            line, column = self.current_token.line, self.current_token.column
            self.advance()
            right = self.addition()
            left = BinaryOpNode(left, op, right, line, column)
            
        return left

    def addition(self) -> ASTNode:
        """解析加减法表达式 (+, -)"""
        left = self.multiplication()
        
        while (self.current_token and self.current_token.type == TokenType.OP and 
               self.current_token.value in (Operator.PLUS.value, Operator.MINUS.value)):
            # 将操作符字符串转换为Operator枚举
            op_value = self.current_token.value
            op = Operator.PLUS if op_value == Operator.PLUS.value else Operator.MINUS
            line, column = self.current_token.line, self.current_token.column
            self.advance()
            right = self.multiplication()
            left = BinaryOpNode(left, op, right, line, column)
            
        return left

    def multiplication(self) -> ASTNode:
        """解析乘除法表达式 (*, /)"""
        left = self.path()
        
        while (self.current_token and self.current_token.type == TokenType.OP and 
               self.current_token.value in (Operator.MULTIPLY.value, Operator.DIVIDE.value)):
            # 将操作符字符串转换为Operator枚举
            op_value = self.current_token.value
            op = Operator.MULTIPLY if op_value == Operator.MULTIPLY.value else Operator.DIVIDE
            line, column = self.current_token.line, self.current_token.column
            self.advance()
            right = self.path()
            left = BinaryOpNode(left, op, right, line, column)
            
        return left

    def path(self) -> ASTNode:
        """解析路径表达式 (obj.key 或 obj[index])"""
        left = self.primary()
        
        def _parse_slice_parts() -> tuple:
            """
            解析切片的end和step部分
            
            返回:
                tuple: (end, step) - 切片的end和step部分
            """
            # 检查是否是第二个冒号，如 [start::step] 或 [::step]
            if self.current_token and self.current_token.type == TokenType.COLON:
                # 是 [start::step] 或 [::step] 形式，end为None
                end = None
                self.advance()  # 跳过第二个冒号
                # 解析step，如果有的话
                step = self.expr() if self.current_token and self.current_token.type != TokenType.RBRACK else None
            else:
                # 是 [start:end] 或 [:end] 形式
                end = self.expr() if self.current_token and self.current_token.type != TokenType.RBRACK else None
                
                # 检查是否有第二个冒号，如 [start:end:step] 或 [:end:step]
                if self.current_token and self.current_token.type == TokenType.COLON:
                    self.advance()  # 跳过第二个冒号
                    step = self.expr() if self.current_token and self.current_token.type != TokenType.RBRACK else None
                else:
                    step = None
            
            return end, step
        
        while self.current_token:
            if self.current_token.type == TokenType.DOT:
                # 字典键访问: obj.key
                self.advance()
                
                # 检查通配符 obj.*
                if self.current_token and self.current_token.type == TokenType.OP and self.current_token.value == '*':
                    line, column = self.current_token.line, self.current_token.column
                    self.advance()
                    left = KeyNode(left, '*', is_wildcard=True, line=line, column=column)
                # 键名可能是NAME或STRING
                elif self.current_token.type == TokenType.NAME:
                    key_name = self.current_token.value
                    line, column = self.current_token.line, self.current_token.column
                    self.advance()
                    left = KeyNode(left, key_name, line=line, column=column)
                elif self.current_token.type == TokenType.STRING:
                    key_name = self.parse_string_literal(self.current_token.value)
                    line, column = self.current_token.line, self.current_token.column
                    self.advance()
                    left = KeyNode(left, key_name, line=line, column=column)
                else:
                    self.error(f"键访问后期望标识符或字符串，但得到了 {self.current_token.type.literal}")
            
            elif self.current_token.type == TokenType.LBRACK:
                # 索引访问: obj[index]
                line, column = self.current_token.line, self.current_token.column
                self.advance()
                
                # 检查是否是通配符索引 obj[*]
                if self.current_token and self.current_token.type == TokenType.OP and self.current_token.value == '*':
                    wildcard_token = self.current_token
                    self.advance()
                    # 确保通配符后面是右括号
                    self.expect(TokenType.RBRACK)
                    # 创建一个特殊的StringNode表示通配符
                    wildcard_node = StringNode('*', wildcard_token.line, wildcard_token.column)
                    left = IndexNode(left, wildcard_node, line, column)
                else:
                    # 检查是否是切片 obj[start:end:step]
                    if self.current_token and self.current_token.type == TokenType.COLON:
                        # 是 [:end:step] 形式，start为None
                        start = None
                        self.advance()  # 跳过第一个冒号
                        end, step = _parse_slice_parts()
                        self.expect(TokenType.RBRACK)
                        left = SliceNode(left, start, end, step, line, column)
                    else:
                        # 先解析第一个表达式
                        index_expr = self.expr()
                        
                        # 检查是否有冒号，表示这是切片的开始
                        if self.current_token and self.current_token.type == TokenType.COLON:
                            # 是 [start:end:step] 形式
                            start = index_expr
                            self.advance()  # 跳过冒号
                            end, step = _parse_slice_parts()
                            self.expect(TokenType.RBRACK)
                            left = SliceNode(left, start, end, step, line, column)
                        else:
                            # 普通索引访问 obj[index]
                            self.expect(TokenType.RBRACK)
                            left = IndexNode(left, index_expr, line, column)
            
            else:
                # 不是路径访问操作，跳出循环
                break
                
        return left

    def primary(self) -> ASTNode:
        """解析基本表达式（变量、脚本调用、字面量等）"""
        if not self.current_token:
            self.error("意外结束，期望表达式")
        
        token = self.current_token
        
        # 检查是否是单独的通配符(*)
        if token.type == TokenType.OP and token.value == '*':
            line, column = token.line, token.column
            self.advance()
            # 创建一个特殊的通配符节点
            # 这里使用一个空的名字，不依赖于特定键名
            root_node = NameNode('', line=line, column=column)
            # 添加一个标记，表示这是根级别的通配符
            root_node._is_root_wildcard = True
            return KeyNode(root_node, '*', is_wildcard=True, line=line, column=column)
        
        # 检查负号开头的负数
        if token.type == TokenType.OP and token.value == '-':
            line, column = token.line, token.column
            self.advance()
            
            # 确保负号后面跟着数字
            if self.current_token and self.current_token.type == TokenType.NUMBER:
                number_token = self.current_token
                value = "-" + number_token.value
                self.advance()
                return NumberNode(value, line, column)
            else:
                # 如果不是负数，回退到上一个token（负号），让正常的二元操作处理
                self.current -= 1
                self.current_token = token
        
        if token.type == TokenType.VARSIGN:
            # 变量引用: $name
            line, column = token.line, token.column
            self.advance()
            name_token = self.expect(TokenType.NAME)
            name_node = NameNode(name_token.value, name_token.line, name_token.column)
            return VarRefNode(name_node, line, column)
            
        elif token.type == TokenType.SCRIPTSIGN:
            # 脚本调用: @func(args)
            line, column = token.line, token.column
            self.advance()
            name_token = self.expect(TokenType.NAME)
            name_node = NameNode(name_token.value, name_token.line, name_token.column)
            
            # 解析参数列表 (...)
            args = []
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                self.advance()
                
                # 解析参数
                if self.current_token and self.current_token.type != TokenType.RPAREN:
                    # 解析第一个参数
                    args.append(self.expr())  # 使用expr()而不是comparison()
                    
                    # 解析逗号分隔的后续参数
                    while self.current_token and self.current_token.type == TokenType.COMMA:
                        self.advance()
                        args.append(self.expr())  # 使用expr()而不是comparison()
                
                # 确保参数列表以右括号结束
                if not self.current_token or self.current_token.type != TokenType.RPAREN:
                    self.error("脚本调用参数列表没有正确结束，期望')'")
                    
                self.advance() # 跳过右括号
            
            return ScriptCallNode(name_node, args, line, column)
            
        elif token.type == TokenType.NAME:
            # 标识符或键名: name
            name = token.value
            line, column = token.line, token.column
            self.advance()
            return NameNode(name, line, column)
            
        elif token.type == TokenType.NUMBER:
            # 数字字面量: 123, 45.67
            value = token.value
            line, column = token.line, token.column
            self.advance()
            
            return NumberNode(value, line, column)
            
        elif token.type == TokenType.STRING:
            # 字符串字面量: "text", 'text'
            value = self.parse_string_literal(token.value)
            line, column = token.line, token.column
            self.advance()
            return StringNode(value, line, column)
            
        elif token.type == TokenType.LPAREN:
            # 括号表达式: (expr)
            self.advance()
            expr = self.expr()
            
            if not self.current_token or self.current_token.type != TokenType.RPAREN:
                self.error("括号表达式没有正确结束，期望')'")
            
            self.advance() # 跳过右括号
            return expr
            
        else:
            self.error(f"意外的令牌类型: {token.type.literal}")

    def parse_string_literal(self, string_literal: str) -> str:
        """解析字符串字面量，去除引号并处理转义字符"""
        # 去除开头和结尾的引号
        inside = string_literal[1:-1]
        
        # 简单处理转义字符
        result = ""
        i = 0
        while i < len(inside):
            if inside[i] == '\\' and i + 1 < len(inside):
                # 处理转义字符
                if inside[i+1] in ('"', "'", '\\'):
                    result += inside[i+1]
                    i += 2
                else:
                    # 不是我们处理的转义字符，保留原样
                    result += inside[i:i+2]
                    i += 2
            else:
                result += inside[i]
                i += 1
                
        return result 
    
    @staticmethod
    def dump_ast(node, annotate_fields=True, indent=None, level=0):
        """
        将AST节点转换为字符串表示
        
        Args:
            node: 要转换的AST节点
            annotate_fields: 是否注释字段
            indent: 缩进级别
            level: 当前节点层级
        """
        def is_ast_node(obj):
            return hasattr(obj, '__class__') and hasattr(obj, '__dict__') and isinstance(obj, ASTNode)

        def format_node(node, level):
            pad = ' ' * (indent * level) if indent else ''
            next_pad = ' ' * (indent * (level + 1)) if indent else ''
            cls_name = node.__class__.__name__
            fields = [(k, v) for k, v in node.__dict__.items() if not k.startswith('_')]
            if not fields:
                return f"{cls_name}()"
            
            # 根据indent决定分隔符
            sep = '' if indent is None else '\n'
            field_sep = ', ' if indent is None else ',\n'
            
            lines = [f"{cls_name}("]
            for i, (k, v) in enumerate(fields):
                if isinstance(v, list):
                    if not v:
                        value_str = '[]'
                    else:
                        list_sep = ', ' if indent is None else ',\n'
                        list_pad = '' if indent is None else next_pad
                        value_str = '[' + list_sep.join(
                            list_pad + (format_node(item, level + 1) if is_ast_node(item) else repr(item))
                            for item in v
                        ) + ']'
                        if indent is not None:
                            value_str = '[\n' + value_str + f'\n{pad}]'
                elif is_ast_node(v):
                    value_str = format_node(v, level + 1)
                else:
                    value_str = repr(v)
                    
                if annotate_fields:
                    lines.append(f"{next_pad}{k}={value_str}")
                else:
                    lines.append(f"{next_pad}{value_str}")
                    
            lines.append(f"{pad})")
            return sep.join(lines)
        return format_node(node, level)