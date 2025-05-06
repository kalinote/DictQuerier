from dictquerier import query_json, flatten_list, script_manager

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
            "items": [
                {
                    "value": 10,
                    "sub_value": 100
                },
                {
                    "value": 20,
                    "sub_value": 200
                },
                {
                    "value": 30,
                    "sub_value": 300
                }
            ],
            "array": [['a', 'b', 'c'], ['d', 'e', 'f']],
            "dictionary": {"key": "value", "invalid": None},
            "list": [
                {"id": 1, "name": "value1", "sub_id": "A", "sub_list": [5,6,7,8]},
                {"id": 2, "name": "value2", "sub_id": "A", "sub_list": [1,2,3,4]},
                {"id": 3, "name": "value3", "sub_id": "B", "sub_list": [9,10,11,12]},
                {"id": 2, "name": "value4", "sub_id": "B", "key": True, "sub_list": [5,6,7,8]}
            ],
            "number_list": [1,2,3,4,5,6,7,8,9]
        }
    }
    
    # 定义测试用例: (路径, 期望结果或异常类型)
    test_cases = [
        # 基本路径查询
        ("root.root_key", "root_value"),            # 点路径查询
        ('root["root_key"]', "root_value"),         # 方括号查询
        ("root['.']", "pass"),                      # 以点为键的方括号查询
        ("root['key.01']", "value"),                # 键包含点的方括号查询
        ("root['key[02]']", "value2"),              # 其他特殊字符的方括号查询
        ("root['dictionary']['key']", "value"),     # 连续方括号查询
        (".root.root_key", "root_value"),            # 以点开头的查询
        
        # 索引和切片
        ("root.number_list[2]", 3),
        
        ("root.root_key", "root_value"),
        ("root.child[0][0]", "first"),
        ("root.items[*].value", [10, 20, 30]),
        ("root.data[*].id", [1, 2, 3]),
        ("root.info.list[1].details", "detail_value"),
        ("root.empty[*]", []),
        ("root.array[1][2]", "f"),
        ("root.dictionary['key']", "value"),
        ("root.list['id'==2].name", ["value2", "value4"]),
        ("root.list[id==1].name", NameError),
        ("root.child[1][0]", "third"),
        ("root['key[02]']", "value2"),
        ("root['.']", "pass"),
        ("root.dictionary['invalid']", None),
        ("root.list['sub_id'=='A'].sub_list", [[5, 6, 7, 8], [1, 2, 3, 4]]),
        ('root.list["id"<3].name', ["value1", "value2", "value4"]),
        ('root.list["id"==2&&"name"=="value4"].sub_list', [[5, 6, 7, 8]]),
        ('root.list["id"==2||"id"==3].sub_id', ["A", "B", "B"]),
        ('root.list[("id"==2||"id"==3)].sub_id', ["A", "B", "B"]),
        (".root.child[1][0]", "third"),
        ("root.number_list[1:4]", [2, 3, 4]),  # 基本切片
        ("root.number_list[::2]", [1, 3, 5, 7, 9]),  # 步长为2
        ("root.number_list[::-1]", [9, 8, 7, 6, 5, 4, 3, 2, 1]),  # 反向切片
        ("root.number_list[-3:]", [7, 8, 9]),  # 负数索引
        ("root.number_list[:3]", [1, 2, 3]),  # 省略start
        ("root.number_list[3:]", [4, 5, 6, 7, 8, 9]),  # 省略end
        ("root.number_list[1:6:2]", [2, 4, 6]),  # 完整切片语法
        ("root.list[1:3].name", ["value2", "value3"]),  # 在对象列表上切片
        ("root.array[0][1:3]", ["b", "c"]),  # 在嵌套列表上切片
        ("root.empty[1:3]", []),  # 在空列表上切片
        ("root.number_list[10:20]", []),  # 超出范围的切片
        ("root.number_list[-10:-5]", [1, 2, 3, 4]),  # 修正期望值
        ("root.number_list[5:2:-1]", [6, 5, 4]),  # 反向步长切片
        ("root.number_list[2:5:0]", ValueError),  # 步长为0（非法）
        ("root.number_list[2:5:1.5]", ValueError),  # 非整数步长（非法）
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
