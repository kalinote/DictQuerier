from dictquerier import query_json, flatten_list, script_manager
from dictquerier.exceptions import JsonPathError

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
            "number_list": [1,2,3,4,5,6,7,8,9],
            8407: "数字键测试",
            "非ASCII键": "中文键值测试",
            "8407": "字符串数字键测试",
            # 正则表达式专用测试数据
            "regex": {
                # 基础类型测试
                "123": "纯数字键",
                "abc": "纯字母键",
                "abc123": "字母数字混合键",
                "key.special": "带点特殊键",
                "中文键": "中文字符键",
                "email@example.com": "电子邮件格式键",
                
                # 键为数字格式的嵌套结构
                "user_001": {"name": "张三", "age": 25, "role": "admin"},
                "user_002": {"name": "李四", "age": 30, "role": "user"},
                "user_003": {"name": "王五", "age": 35, "role": "user"},
                "admin_001": {"name": "管理员1", "permissions": ["read", "write", "delete"]},
                "admin_002": {"name": "管理员2", "permissions": ["read", "write"]},
                
                # 键为特殊格式的嵌套结构
                "api/v1/users": [
                    {"id": 1, "username": "user1"},
                    {"id": 2, "username": "user2"}
                ],
                "api/v1/posts": [
                    {"id": 101, "title": "文章1"},
                    {"id": 102, "title": "文章2"}
                ],
                "api/v2/users": [
                    {"id": 3, "username": "user3"},
                    {"id": 4, "username": "user4"}
                ],
                
                # 包含点号的复杂键
                "config.dev": {"host": "localhost", "port": 8080},
                "config.prod": {"host": "example.com", "port": 443},
                
                # 更复杂的嵌套结构
                "nested.data.001": {
                    "level1": {
                        "level2": {
                            "level3": "深度嵌套数据1"
                        }
                    }
                },
                "nested.data.002": {
                    "level1": {
                        "level2": {
                            "level3": "深度嵌套数据2"
                        }
                    }
                }
            }
        }
    }
    # 定义测试用例: (路径, 期望结果或异常类型)
    test_cases = [
        # # 基本路径查询
        # ("root.root_key", "root_value"),          # 点操作符查询
        # ('root["root_key"]', "root_value"),       # 方括号查询
        # ("root.8407", "数字键测试"),                # 整数类型数据方括号查询
        # ("root[8407]", "数字键测试"),               # 整数类型数据点操作符查询
        # ('root."8407"', "字符串数字键测试"),         # 数字字符串点操作符查询
        # ('root["8407"]', "字符串数字键测试"),        # 数字字符串方括号查询
        # ("root.\.", "pass"),                      # 以点为键的点操作符查询
        # ("root['.']", "pass"),                    # 以点为键的方括号查询
        # ("root['key.01']", "value"),              # 键包含点的方括号查询
        # ("root.key\.01", "value"),                # 键包含点的点操作符查询
        
        # # 索引和切片
        # ("root.number_list[2]", 3),
        
        # # 正则表达式测试
        # # 1. 基本匹配测试
        # (r"root.regex['^[0-9]+$']", ["纯数字键"]),  # 完全匹配纯数字键
        # (r"root.regex['^[a-z]+$']", ["纯字母键"]),  # 完全匹配纯字母键
        
        # # 2. 嵌套结构匹配 - 返回对象
        # (r"root.regex['^user_\\d+$']", [
        #     {"name": "张三", "age": 25, "role": "admin"},
        #     {"name": "李四", "age": 30, "role": "user"},
        #     {"name": "王五", "age": 35, "role": "user"}
        # ]),  # 匹配所有用户对象
        
        # # 3. 嵌套结构匹配 - 返回数组
        # (r"root.regex['^api/v1/']", [
        #     [{"id": 1, "username": "user1"}, {"id": 2, "username": "user2"}],
        #     [{"id": 101, "title": "文章1"}, {"id": 102, "title": "文章2"}]
        # ]),  # 匹配所有v1 API数据
        
        # # 4. 带点号的键匹配
        # (r"root.regex['^config\\.']", [
        #     {"host": "localhost", "port": 8080},
        #     {"host": "example.com", "port": 443}
        # ]),  # 匹配所有配置数据
        
        # # 5. 复杂嵌套结构匹配
        # (r"root.regex['^nested\\.data']", [
        #     {
        #         "level1": {
        #             "level2": {
        #                 "level3": "深度嵌套数据1"
        #             }
        #         }
        #     },
        #     {
        #         "level1": {
        #             "level2": {
        #                 "level3": "深度嵌套数据2"
        #             }
        #         }
        #     }
        # ]),  # 匹配所有深度嵌套数据
        
        # # 6. 多层嵌套正则匹配后继续查询
        # (r"root.regex['^user_\\d+$'].name", ["张三", "李四", "王五"]),  # 匹配用户后获取名称
        
        # # 7. 复杂正则表达式
        # (r"root.regex.^admin_\\d+$.permissions", [
        #     ["read", "write", "delete"],
        #     ["read", "write"]
        # ]),  # 匹配管理员权限
        
        # ("root.root_key", "root_value"),
        # ("root.child[0][0]", "first"),
        # (r"root.key\.01", "value"),
        # ("root.items[*].value", [10, 20, 30]),
        # ("root.data[*].id", [1, 2, 3]),
        # ("root.info.list[1].details", "detail_value"),
        # ("root.empty[*]", []),
        # ("root.array[1][2]", "f"),
        # ("root.dictionary['key']", "value"),
        # ("root.list['id'==2].name", ["value2", "value4"]),
        # ("root.list[id==1].name", ['value1']),
        # ("root.child[1][0]", "third"),
        # ("root['key[02]']", "value2"),
        # ("root['.']", "pass"),
        # ("root.dictionary['invalid']", None),
        # ("root.list['sub_id'=='A'].sub_list", [[5, 6, 7, 8], [1, 2, 3, 4]]),
        # ('root.list["id"<3].name', ["value1", "value2", "value4"]),
        # ('root.list["id"==2&&"name"=="value4"].sub_list', [[5, 6, 7, 8]]),
        # ('root.list["id"==2||"id"==3].sub_id', ["A", "B"]),
        # ('root.list[("id"==2||"id"==3)].sub_id', ["A", "B"]),
        # (".root.child[1][0]", "third"),
        # ("root.number_list[1:4]", [2, 3, 4]),  # 基本切片
        # ("root.number_list[::2]", [1, 3, 5, 7, 9]),  # 步长为2
        # ("root.number_list[::-1]", [9, 8, 7, 6, 5, 4, 3, 2, 1]),  # 反向切片
        # ("root.number_list[-3:]", [7, 8, 9]),  # 负数索引
        # ("root.number_list[:3]", [1, 2, 3]),  # 省略start
        # ("root.number_list[3:]", [4, 5, 6, 7, 8, 9]),  # 省略end
        # ("root.number_list[1:6:2]", [2, 4, 6]),  # 完整切片语法
        # ("root.list[1:3].name", ["value2", "value3"]),  # 在对象列表上切片
        # ("root.array[0][1:3]", ["b", "c"]),  # 在嵌套列表上切片
        # ("root.empty[1:3]", []),  # 在空列表上切片
        # ("root.number_list[10:20]", []),  # 超出范围的切片
        # ("root.number_list[-10:-5]", [1, 2, 3, 4]),  # 修正期望值
        # ("root.number_list[5:2:-1]", [6, 5, 4]),  # 反向步长切片
        # ("root.number_list[2:5:0]", ValueError),  # 步长为0（非法）
        # ("root.number_list[2:5:1.5]", ValueError),  # 非整数步长（非法）
        # ("root.8407", "数字键测试"),                 # 数字键测试
        # ("root.'8407'", "字符串数字键测试"),        # 单引号字符串数字键测试
        # ("root.'非ASCII键'", "中文键值测试"),        # 单引号中文键值测试
        # ('root."8407"', "字符串数字键测试"),        # 双引号字符串数字键测试
        # ('root[8407]', "数字键测试"),                # 数字键测试
        # ('root["非ASCII键"]', "中文键值测试"),        # 方括号中文键值测试
        # ('root.items["value">@bigger_than(15)].sub_value', NotImplementedError),
        ('root.list[( "id"==2 && "name"=="value4" ) || ( "id"==2 && "sub_id" == "A" )].sub_list', [[5, 6, 7, 8], [1, 2, 3, 4]]),
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

@script_manager.register(name="bigger_than")
def bigger_than(value):
    print("执行脚本测试")
    return value

if __name__ == "__main__":
    main()
