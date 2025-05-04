import re
from dictquerier.tokenizer.token import Token
from dictquerier.tokenizer.enum import TokenType


class Lexer:
    """
    词法分析器，将文本转换为 Token 序列
    """
    def __init__(self, text):
        # 预处理：将 .[key] 转换为 .key
        self.original_text = text
        self.text = self._preprocess_text(text)
        self.pos = 0
        self.line = 1
        self.column = 0

        # 基于 TokenType 构造 master_pattern，排除 END
        patterns = [f"(?P<{t.name}>{t.pattern})"
                    for t in TokenType]
        self.master_pattern = re.compile("|".join(patterns))

    def _preprocess_text(self, text):
        """预处理文本，转换特殊语法形式"""
        return re.sub(r'\.(?=\[)', r'.*', text)

    def tokenize(self):
        # 如果以点开头，在开头插入一个*通配符
        if self.text.lstrip().startswith('.'):
            # 创建一个人工的通配符Token
            yield Token(TokenType.OP, '*', column=0, line=1)
        
        for m in self.master_pattern.finditer(self.text):
            kind = m.lastgroup
            value = m.group(kind)

            # 更新行列号
            self._update_position(value)
            
            # 跳过空白符
            if kind == 'WHITESPACE':
                continue
            
            # 未知字符时报错
            if kind == 'UNKNOWN':
                raise SyntaxError(f"非法字符 {value!r} 在行{self.line}, 列{self.column}")

            tok_type = TokenType[kind]
            yield Token(tok_type, value, column=self.column, line=self.line)

        # 扫描结束后，附加 END token
        yield Token(TokenType.END, None, column=self.column, line=self.line)

    def _update_position(self, text):
        """
        根据文本内容更新行号和列号
        """
        lines = text.split('\n')
        if len(lines) > 1:
            self.line += len(lines) - 1
            self.column = len(lines[-1])
        else:
            self.column += len(text)
