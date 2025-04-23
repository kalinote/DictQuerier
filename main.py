from jsonquerier import query_json, flatten_list

def main():
    # 生成用于测试的示例JSON数据
    test_data = {
        "root": {
            "root_key": "root_value",
            "child": [
                ["first", "second"],
                ["third", "fourth"]
            ],
            "key.01": "value",
            "key[02]": "value2",
            ".": "pass",
            "exception": {"error": "trigger"},
            "data": [{"id": 1}, {"id": 2}, {"id": 3}],
            "info": {"list": ["first_list_item", {"details": "detail_value"}]},
            "empty": [],
            "items": [{"value": 10}, {"value": 20}, {"value": 30}],
            "array": [['a', 'b', 'c'], ['d', 'e', 'f']],
            "dictionary": {"key": "value", "invalid": None},
            "list": [
                {"id": 1, "name": "value1", "sub_id": "A", "sub_list": [5,6,7,8]},
                {"id": 2, "name": "value2", "sub_id": "A", "sub_list": [1,2,3,4]},
                {"id": 3, "name": "value3", "sub_id": "B", "sub_list": [9,10,11,12]},
                {"id": 2, "name": "value4", "sub_id": "B", "key": True, "sub_list": [5,6,7,8]}
            ],
            "number_list": [1,2,3,4,5,6,7,8,9],
            8407: "数字键测试",
            "非ASCII键": "中文键值测试",
            "8407": "字符串数字键测试"
        }
    }
    # 定义测试用例: (路径, 期望结果或异常类型)
    test_cases = [
        # 基本路径查询
        ("root.root_key", "root_value"),
        ('root["root_key"]', "root_value"),
        ("root.root_key", "root_value"),
        ("root.root_key", "root_value"),
        ("root.8407", "数字键测试"),
        ("root[8407]", "数字键测试"),
        ('root."8407"', "字符串数字键测试"),
        ('root["8407"]', "字符串数字键测试")

    ]
    # 统计变量
    total = len(test_cases)
    success = 0
    fail_cases = []

    # 遍历测试用例并输出结果
    for path, expected in test_cases:
        try:
            result = query_json(test_data, path)
            # 判断期望是否为异常类型
            if isinstance(expected, type) and issubclass(expected, Exception):
                print(f"测试失败: {path} 未抛出预期异常 {expected.__name__}")
                fail_cases.append((path, f"未抛出预期异常 {expected.__name__}", None))
            elif result == expected:
                print(f"测试通过: {path} -> {result}")
                success += 1
            else:
                print(f"测试失败: {path} -> {result}, 期望: {expected}")
                fail_cases.append((path, result, expected))
        except Exception as e:
            if isinstance(expected, type) and isinstance(e, expected):
                print(f"测试通过: {path} -> 抛出预期异常 {e}")
                success += 1
            else:
                print(f"测试失败: {path} -> 抛出异常 {e}, 期望: {expected}")
                fail_cases.append((path, f"抛出异常 {e}", expected))

    # 输出成功率统计
    print("\n==============================")
    print(f"测试总数: {total}，通过数: {success}，失败数: {total - success}")
    print(f"成功率: {success / total * 100:.2f}%")
    if fail_cases:
        print("\n以下为所有测试失败的用例：")
        for idx, (path, got, expected) in enumerate(fail_cases, 1):
            print(f"{idx}. 路径: {path}")
            print(f"   实际结果: {got}")
            print(f"   期望结果: {expected}")
    print("==============================\n")

    # 测试 flatten_list 函数
    print("flatten_list 测试:")
    flat_cases = [
        ([[1, [2, [3, 4]]], [5]], [1, 2, 3, 4, 5]),
        ([], []),
        ([1, 2, 3], [1, 2, 3])
    ]
    flat_total = len(flat_cases)
    flat_success = 0
    flat_fail_cases = []
    for nested, expected in flat_cases:
        result = flatten_list(nested)
        if result == expected:
            print(f"flatten_list 测试通过: {nested} -> {result}")
            flat_success += 1
        else:
            print(f"flatten_list 测试失败: {nested} -> {result}, 期望: {expected}")
            flat_fail_cases.append((nested, result, expected))
    print("\n------------------------------")
    print(f"flatten_list 测试总数: {flat_total}，通过数: {flat_success}，失败数: {flat_total - flat_success}")
    print(f"flatten_list 成功率: {flat_success / flat_total * 100:.2f}%")
    if flat_fail_cases:
        print("\n以下为所有 flatten_list 测试失败的用例：")
        for idx, (nested, got, expected) in enumerate(flat_fail_cases, 1):
            print(f"{idx}. 输入: {nested}")
            print(f"   实际结果: {got}")
            print(f"   期望结果: {expected}")
    print("------------------------------\n")

if __name__ == "__main__":
    main()
