"""
核心查询功能
"""
import re
from typing import Any, Union, List, Dict

from dictquerier.expression.base import BaseExpression

from .exceptions import JsonPathError
from .operator.enum import Operator
from .path.parser import PathParser

def query_json(
    data: Union[Dict, List], 
    path: str, 
    no_path_exception: bool = False,
    no_regex: bool = False
) -> Any:
    r"""查询json数据

    Args:
        data (Union[Dict, List]): 需要查询的json结构
        path (str): 查询路径语句
        no_path_exception (bool, optional): 关闭报错，该项设置为True时，查询出错不会产生报错，而是返回空列表[]. Defaults to False.
        no_regex (bool, optional): TODO 关闭正则表达式匹配，该项设置为True时，不会进行任何正则表达式匹配，如果查询路径中包含正则表达式，会直接报错。Defaults to False.

    Raises:
        ValueError: 查询值类型错误
        JsonPathError: 查询路径错误
        SyntaxError: 查询语句错误

    Returns:
        Any: 查询结果
    """
    path = path.strip()
    if path == '':
        return data
    
    # TODO 增加对 JSON Path 的兼容支持
    json_path = False
    if path.startswith('$'):
        json_path = True
        path = path[1:]
    
    nodes = PathParser.parse(path)
    current = data
    try:
        for idx, node in enumerate(nodes):
            # 临时过渡
            node = node.get_value()
            if node == '*':
                # 处理简单通配符
                if isinstance(current, list):
                    results = [query_json(item, PathParser.nodes2path(nodes[idx+1:]), no_path_exception=True, no_regex=no_regex) for item in current]
                    if all(result == [] for result in results):
                        return []
                    return [result for result in results if result != []]
                elif isinstance(current, dict):
                    current = list(current.values())
                else:
                    raise ValueError(f"通配符位置错误，当前数据不是列表: {current}")
            elif isinstance(current, list) and isinstance(node, int):
                # 基础列表索引解析
                if node >= len(current):
                    raise IndexError(f"数组访问越界: < {node} >")
                current = current[node]
            elif isinstance(current, dict):
                # 字典解析
                # TODO 增加key刚好是正则表达式的情况处理
                if node in current:
                    current = current[node]
                else:
                    
                    # 正则表达式处理
                    try:
                        regex = re.compile(node)
                    except re.error as e:
                        raise JsonPathError(f"路径错误或类型不匹配，或者是不合法的正则表达式：<{node}>")
                    matching_nodes = [item for item in current.keys() if regex.search(str(item))]
                    
                    if len(matching_nodes) == 0:
                        raise JsonPathError(f"已解析正则表达式，但未找到匹配的元素：<{node}>")
                    
                    # 如果有后续路径，则为每个匹配元素递归应用
                    if idx < len(nodes) - 1:
                        results = []
                        for item in matching_nodes:
                            item_result = query_json(current[item], PathParser.nodes2path(nodes[idx+1:]), no_path_exception=True, no_regex=no_regex)
                            if item_result != []:
                                results.append(item_result)
                        return results if results else []
                    else:
                        # 没有后续路径，直接返回所有匹配元素的值
                        return [current[item] for item in matching_nodes]
            elif isinstance(current, list) and isinstance(node, BaseExpression):
                # 复杂表达式解析
                result_list = []

                try:
                    # FIXME 多层逻辑表达式存在查询问题
                    itempack_list = node.operate(current)
                except Exception as e:
                    raise SyntaxError(f"表达式操作失败: {str(e)}")
                    
                if not isinstance(itempack_list, (list, tuple)):
                    itempack_list = [itempack_list]
                    
                for item in itempack_list:
                    item_result = query_json(item, PathParser.nodes2path(nodes[idx+1:]), 
                                        no_path_exception=True, no_regex=no_regex)
                    if item_result not in result_list:
                        result_list.append(item_result)
                return result_list
            else:
                raise JsonPathError(f"路径错误或类型不匹配：<{node}>")
    except JsonPathError as e:
        if no_path_exception:
            return []
        else:
            raise e
    except (KeyError, IndexError, TypeError, ValueError) as e:
        if no_path_exception:
            return []
        else:
            # 增加表达式错误的处理
            if isinstance(node, BaseExpression):
                raise JsonPathError(f"表达式执行错误：<{node.get_expression()}>，错误信息：{str(e)}")
            else:
                raise JsonPathError(f"路径错误：<{node}>，错误信息：{str(e)}")
    return current

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