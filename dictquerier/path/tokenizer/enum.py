
from enum import Enum, auto


class TokenType(Enum):
    """
    词法分析器返回的token类型
    """
    VARSIGN    = ("$", r"\$")                           # 变量符号
    SCRIPTSIGN = ("@", r"@")                            # 脚本符号
    WILDCHAR   = ("*", r"\*")                           # 通配符
    DOT        = (".", r"\.")                           # .
    WHITESPACE = ("whitespace", r"\s+")                 # 空白符
    NAME       = ("name", r"[a-zA-Z_][a-zA-Z0-9_]*")    # 标识符，比如 root、child
    NUMBER     = ("number", r"\d+(\.\d+)?")             # 整数或浮点
    STRING     = ("string", r'"[^"]*"')                 # 引号字符串
    LBRACK     = ("[", r"\[")                           # [
    RBRACK     = ("]", r"\]")                           # ]
    LPAREN     = ("(", r"\(")                           # (
    RPAREN     = (")", r"\)")                           # )
    COLON      = (":", r":")                            # :
    COMMA      = (",", r",")                            # ,
    OP         = ("op", r"==|!=|>=|<=|>|<|&&|\|\||[+\-*/=<>]")    # 操作符，比如 ==, >, <, *, &&, ||等
    END        = ("end", r"$^")                         # 结束
    
    def __init__(self, literal, pattern):
        self._literal = literal
        self._pattern = pattern

    @property
    def literal(self):
        return self._literal

    @property
    def pattern(self):
        return self._pattern
    