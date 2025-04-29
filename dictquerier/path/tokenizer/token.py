from dictquerier.path.tokenizer.enum import TokenType


class Token:
    def __init__(self, type: TokenType, value, column=None, line=None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, at {self.column} line {self.line})'
