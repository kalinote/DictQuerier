import re
from dictquerier.path.tokenizer.token import Token
from dictquerier.path.tokenizer.enum import TokenType


class Lexer:
    """
    词法分析器，将文本转换为 Token 序列
    """
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 0

        # 基于 TokenType 构造 master_pattern，排除 END
        patterns = [f"(?P<{t.name}>{t.pattern})"
                    for t in TokenType]
        self.master_pattern = re.compile("|".join(patterns))

    def tokenize(self):
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
