from dictquerier.path.tokenizer.token import Token
from dictquerier.path.tokenizer.enum import TokenType
import re

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.tokens = []
        
        self.token_exprs = [
            (token_type, re.compile(token_type.pattern))
            for token_type in TokenType
        ]

    def tokenize(self):
        while self.pos < len(self.text):
            match = None
            for token_type, pattern in self.token_exprs:
                match = pattern.match(self.text, self.pos)
                if match:
                    value = match.group(0)
                    # 忽略空白符
                    if token_type != TokenType.WHITESPACE:
                        token = Token(token_type, value, self.pos)
                        self.tokens.append(token)
                    self.pos = match.end()
                    break
            if not match:
                raise SyntaxError(f'非法字符: {self.text[self.pos]!r} at position {self.pos}')
        
        # 最后加一个 END token
        self.tokens.append(Token(TokenType.END, None, self.pos))
        return self.tokens
