from typing import List, Optional, Iterator
from dictquerier.path.tokenizer.token import Token
from dictquerier.path.tokenizer.enum import TokenType
from dictquerier.path.syntax_tree.node import (
    ASTNode, NameNode, NumberNode, StringNode, VarRefNode,
    ScriptCallNode, BinaryOpNode, AttributeNode, IndexNode
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
        
        result = self.expr()
        
        # 确保所有令牌都已解析（除了END）
        if self.current_token and self.current_token.type != TokenType.END:
            self.error(f"解析结束后仍有未处理的令牌: {self.current_token}")
            
        return result

    def error(self, message: str):
        """抛出语法错误异常"""
        line = self.current_token.line if self.current_token else "未知"
        column = self.current_token.column if self.current_token else "未知"
        raise SyntaxError(f"{message}，在行{line}列{column}")

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
        
        while self.current_token and self.current_token.type == TokenType.OP and self.current_token.value in ('||', '&&'):
            op = self.current_token.value
            line, column = self.current_token.line, self.current_token.column
            self.advance()
            right = self.comparison()
            left = BinaryOpNode(left, op, right, line, column)
            
        return left

    def comparison(self) -> ASTNode:
        """解析比较表达式 (>, <, >=, <=, ==, !=)"""
        left = self.addition()
        
        while (self.current_token and self.current_token.type == TokenType.OP and 
               self.current_token.value in ('>', '<', '>=', '<=', '==', '!=')):
            op = self.current_token.value
            line, column = self.current_token.line, self.current_token.column
            self.advance()
            right = self.addition()
            left = BinaryOpNode(left, op, right, line, column)
            
        return left

    def addition(self) -> ASTNode:
        """解析加减法表达式 (+, -)"""
        left = self.multiplication()
        
        while (self.current_token and self.current_token.type == TokenType.OP and 
               self.current_token.value in ('+', '-')):
            op = self.current_token.value
            line, column = self.current_token.line, self.current_token.column
            self.advance()
            right = self.multiplication()
            left = BinaryOpNode(left, op, right, line, column)
            
        return left

    def multiplication(self) -> ASTNode:
        """解析乘除法表达式 (*, /)"""
        left = self.path()
        
        while (self.current_token and self.current_token.type == TokenType.OP and 
               self.current_token.value in ('*', '/')):
            op = self.current_token.value
            line, column = self.current_token.line, self.current_token.column
            self.advance()
            right = self.path()
            left = BinaryOpNode(left, op, right, line, column)
            
        return left

    def path(self) -> ASTNode:
        """解析路径表达式 (obj.attr 或 obj[index])"""
        left = self.primary()
        
        while self.current_token:
            if self.current_token.type == TokenType.DOT:
                # 属性访问: obj.attr
                self.advance()
                
                # 属性名可能是NAME或STRING
                if self.current_token.type == TokenType.NAME:
                    attr_name = self.current_token.value
                    line, column = self.current_token.line, self.current_token.column
                    self.advance()
                    left = AttributeNode(left, attr_name, line, column)
                elif self.current_token.type == TokenType.STRING:
                    attr_name = self.parse_string_literal(self.current_token.value)
                    line, column = self.current_token.line, self.current_token.column
                    self.advance()
                    left = AttributeNode(left, attr_name, line, column)
                else:
                    self.error(f"属性访问后期望标识符或字符串，但得到了 {self.current_token.type.literal}")
            
            elif self.current_token.type == TokenType.LBRACK:
                # 索引访问: obj[index]
                line, column = self.current_token.line, self.current_token.column
                self.advance()
                
                index_expr = self.expr()  # 索引可以是任意表达式
                
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
            # 标识符: name
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