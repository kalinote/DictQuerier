from enum import Enum, auto


class TokenType(Enum):
    """
    词法分析器的token类型
    """
    VARSIGN    = ("$", r"\$")                           # 变量符号，这个符号一般来说后面只能跟NAME
    SCRIPTSIGN = ("@", r"@")                            # 脚本符号，这个符号一般来说后面只能跟NAME
    DOT        = (".", r"\.")                           # .
    WHITESPACE = ("whitespace", r"\s+")                 # 空白符，暂时没用，因为在解析时会跳过
    OP         = ("op", r"==|!=|>=|<=|>|<|&&|\|\||[+\-*/=<>]")    # 操作符，比如 ==, >, <, *, &&, ||等
    NAME       = ("name", r"[a-zA-Z_][a-zA-Z0-9_]*")    # 标识符
    NUMBER     = ("number", r"\d+(\.\d+)?([eE][+-]?\d+)?")        # 整数或浮点
    STRING     = ("string", r""""(?:\\.|[^"\\])*"|'(?:\\.|[^\\'])*'""") # 引号字符串
    LBRACK     = ("[", r"\[")                           # [
    RBRACK     = ("]", r"\]")                           # ]
    LPAREN     = ("(", r"\(")                           # (
    RPAREN     = (")", r"\)")                           # )
    COLON      = (":", r":")                            # :
    COMMA      = (",", r",")                            # ,
    END        = ("end", r"$^")                         # 结束
    UNKNOWN    = ("unknown", r".")                      # 未知字符
    
    def __init__(self, literal, pattern):
        self._literal = literal
        self._pattern = pattern

    @property
    def literal(self):
        return self._literal

    @property
    def pattern(self):
        return self._pattern
    