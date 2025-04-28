"""
异常处理模块
"""

class JsonPathError(Exception):
    """自定义异常类，用于JSON路径查询错误。"""
    def __init__(self, message: str):
        super().__init__(message) 
        
class ExpressionParsingError(Exception):
    """表达式解析错误"""
    def __init__(self, message: str):
        super().__init__(message) 

class ScriptNotRegisteredError(Exception):
    """脚本未注册错误"""
    def __init__(self, message: str):
        super().__init__(message) 