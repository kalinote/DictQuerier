"""
异常处理模块
"""

class PathError(Exception):
    """路径查询错误。"""
    def __init__(self, message: str):
        super().__init__(message) 
        
class ExpressionParsingError(Exception):
    """表达式解析错误"""
    def __init__(self, message: str):
        super().__init__(message) 

class UnknowScript(Exception):
    """未知的脚本"""
    def __init__(self, message: str):
        super().__init__(message) 
        
class UnknownOperator(Exception):
    """未知的操作符"""
    def __init__(self, message: str):
        super().__init__(message) 

