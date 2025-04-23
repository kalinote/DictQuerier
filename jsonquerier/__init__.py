"""
JsonQuerier - 基于路径的Json数据查询工具

这个包提供了类似于JSONPath的语法，用于从JSON数据中提取数据。
"""

__version__ = "0.1.0"

from .exceptions import JsonPathError
from .operators import Opreater
from .expression import Expression, parse_path, elements2path
from .core import query_json, flatten_list

__all__ = [
    'JsonPathError', 
    'Opreater', 
    'Expression', 
    'parse_path', 
    'elements2path',
    'query_json', 
    'flatten_list'
] 