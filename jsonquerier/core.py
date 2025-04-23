"""
核心查询功能
"""
from typing import Any, Union, List, Dict

from .exceptions import JsonPathError
from .expression import Expression, parse_path, elements2path
from .operators import Opreater

def query_json(data: Union[Dict, List], path: str, no_path_exception: bool = False) -> Any:
    r"""查询json数据

    Args:
        data (Union[Dict, List]): 需要查询的json结构
        path (str): 查询路径语句
        no_path_exception (bool, optional): 关闭报错，该项设置为True时，查询出错不会产生报错，而是返回空列表[]. Defaults to False.

    Raises:
        ValueError: 查询值类型错误
        JsonPathError: 查询路径错误
        SyntaxError: 查询语句错误

    Returns:
        Any: 查询结果
    """
    elements = parse_path(path)
    current = data
    try:
        for idx, element in enumerate(elements):
            # TODO 增加字符串通配符
            if element == '*':  # 处理简单通配符
                if isinstance(current, list):
                    results = [query_json(item, elements2path(elements[idx+1:]), no_path_exception=True) for item in current]
                    if all(result == [] for result in results):
                        return []
                    return [result for result in results if result != []]
                elif isinstance(current, dict):
                    current = list(current.values())
                else:
                    raise ValueError(f"通配符位置错误，当前数据不是列表: {current}")
            elif isinstance(current, list) and isinstance(element, int):
                # 基础列表索引解析
                if element >= len(current):
                    raise IndexError(f"数组访问越界: <{element}>")
                current = current[element]
            elif isinstance(current, dict) and element in current:
                # 字典解析
                current = current[element]
            elif isinstance(current, list) and isinstance(element, Expression):
                # 复杂表达式解析
                result_list = []
                if not isinstance(element.operator, Opreater):
                    raise SyntaxError(f"不支持的运算符类型: <{type(element.operator).__name__}>")
                
                itempack_list = element.operate(current)
                for item in itempack_list:
                    item_result = query_json(item, elements2path(elements[idx+1:]), no_path_exception=True)
                    if item_result not in result_list:
                        result_list.append(item_result)
                return result_list
            else:
                raise JsonPathError(f"路径错误或类型不匹配：<{element}>")
    except JsonPathError as e:
        if no_path_exception:
            return []
        else:
            raise e
    except (KeyError, IndexError, TypeError, ValueError) as e:
        raise JsonPathError(f"路径错误：<{element}>，错误信息：{str(e)}")
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
    for element in nested_list:
        if isinstance(element, list):
            result.extend(flatten_list(element))  # 递归展开子列表
        else:
            result.append(element)  # 添加非列表元素
    return result 