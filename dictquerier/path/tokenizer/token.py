class Token:
    def __init__(self, type, value, column=None):
        self.type = type
        self.value = value
        # 暂时没有多行查询，line固定为1
        self.line = 1
        self.column = column
    
    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, at {self.column})'
