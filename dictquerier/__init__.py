"""
dictquerier - 基于路径的Json数据查询工具

这个包提供了类似于JSONPath的语法，用于从JSON数据中提取数据。
"""

__version__ = "0.1.0"

from .exceptions import PathError
from .tokenizer.enum import Operator
from .core import query_json, flatten_list

from .script.manager import script_manager



__all__ = [
    'PathError', 
    'Operator', 
    'query_json', 
    'flatten_list',
    'script_manager'
] 