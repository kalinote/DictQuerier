"""
核心查询功能
"""
from typing import Any, Union, List, Dict
from dictquerier.tokenizer.lexer import Lexer
from dictquerier.syntax_tree.parser import Parser
from dictquerier.executor.evaluator import Evaluator

def query_json(
    data: Union[Dict, List], 
    path: str, 
    no_path_exception: bool = False,
) -> Any:
    r"""查询json数据

    Args:
        data (Union[Dict, List]): 需要查询的json结构
        path (str): 查询路径语句
        no_path_exception (bool, optional): 关闭报错，该项设置为True时，查询出错不会产生报错，而是返回空列表[]. Defaults to False.

    Returns:
        Any: 查询结果
    """
    try:
        # 词法分析
        lexer = Lexer(path)
        tokens = list(lexer.tokenize())
        
        # 语法分析
        parser = Parser(tokens)
        ast_root = parser.parse()
        
        # 执行查询
        evaluator = Evaluator(data)
        result = evaluator.query(ast_root)
        
        return result
    
    except Exception as e:
        if no_path_exception:
            return []
        raise e

def flatten_list(nested_list):
    """
    将嵌套的多维列表展开为一维列表。

    Args:
        nested_list: 嵌套的多维列表

    Returns:
        list: 展开后的一维列表
    """
    result = []
    for node in nested_list:
        if isinstance(node, list):
            result.extend(flatten_list(node))  # 递归展开子列表
        else:
            result.append(node)  # 添加非列表元素
    return result 