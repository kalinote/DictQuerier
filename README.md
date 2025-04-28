# DictQuerier

基于路径的Python字典数据查询工具，支持复杂的路径表达式、条件筛选和数据提取。

> [!WARNING]
> 
> 主要用于研究学习，暂时还不兼容 JSON Path 语法，主要是写这个模块的时候我还不知道 JSON Path 这个东西...
> 
> 后续"可能会"逐步增加对 JSON Path 的兼容，但优先级不高。如果有类似的开发需求，请使用标准的 JSON Path

## 特性

- 支持条件表达式过滤
- 支持通配符和切片操作
- 支持正则表达式匹配键名
- 全面的错误处理
- 完善的类型标注
- 提供命令行工具

## 安装

```bash
pip install dictquerier
```

## 快速开始

### Python API

```python
from dictquerier import query_json

# 数据示例
data = {
    "users": [
        {"id": 1, "name": "张三", "scores": [80, 90, 85]},
        {"id": 2, "name": "李四", "scores": [70, 85, 92]},
        {"id": 3, "name": "王五", "scores": [95, 88, 75]}
    ]
}

# 基本查询
result1 = query_json(data, "users[0].name")  # 返回: "张三"

# 通配符查询
result2 = query_json(data, "users[*].name")  # 返回: ["张三", "李四", "王五"]

# 条件表达式查询
result3 = query_json(data, "users['id'==2].name")  # 返回: ["李四"]
result4 = query_json(data, "users['id'>1].name")  # 返回: ["李四", "王五"]

# 复杂条件查询
result5 = query_json(data, "users['id'==1||'id'==3].scores")  # 返回: [[80, 90, 85], [95, 88, 75]]

# 切片操作
result6 = query_json(data, "users[1:3].name")  # 返回: ["李四", "王五"]
result7 = query_json(data, "users[0].scores[::2]")  # 返回: [80, 85]
```

### 命令行工具

安装后可以直接使用命令行工具：

```bash
# 从文件查询
dictquerier -f data.json -p "users[*].name"

# 直接使用JSON字符串
dictquerier -i '{"users":[{"id":1,"name":"张三"}]}' -p "users[0].name"

# 保存结果到文件
dictquerier -f data.json -p "users['id'>1]" -o result.json

# 使用紧凑输出格式
dictquerier -f data.json -p "users[*].name" -c
```

命令行参数：

- `-f, --file`: 要查询的JSON文件路径
- `-p, --path`: 查询路径表达式（必需）
- `-i, --input`: 直接输入的JSON字符串
- `-o, --output`: 输出文件路径（默认为标准输出）
- `-c, --compact`: 输出紧凑的JSON格式

## 语法说明

- `.` 表示子元素访问
- `[数字]` 表示按索引访问
- `[*]` 通配符，表示所有元素
- `[start:end:step]` 切片操作
- `['key'==value]` 条件过滤
- 支持的操作符: `==`, `!=`, `<`, `>`, `<=`, `>=`, `&&`, `||`

## 正则表达式匹配

可以使用正则表达式来匹配JSON对象中的键名：

```python
from dictquerier import query_json

# 数据示例
data = {
    "root": {
        "user_001": {"name": "张三", "age": 25},
        "user_002": {"name": "李四", "age": 30},
        "user_003": {"name": "王五", "age": 35},
        "admin_001": {"name": "管理员1", "permissions": ["read", "write"]},
        "admin_002": {"name": "管理员2", "permissions": ["read"]}
    }
}

# 匹配所有用户
result1 = query_json(data, r"root['^user_\\d+$']")
# 返回: [{"name": "张三", "age": 25}, {"name": "李四", "age": 30}, {"name": "王五", "age": 35}]

# 获取所有匹配用户的名称
result2 = query_json(data, r"root['^user_\\d+$'].name")
# 返回: ["张三", "李四", "王五"]

# 匹配所有管理员的权限(支持点语法，可以不带引号)
result3 = query_json(data, r"root.regex.^admin_\\d+$.permissions")
# 返回: [["read", "write"], ["read"]]
```

正则表达式语法：

- 直接在查询语句中编写正则表达式即可
- 支持标准的Python正则表达式语法
- 特殊字符（如 `.` 和 `\`）需要正确转义
- 匹配成功后返回的是所有匹配键对应的值组成的列表

## 错误处理

```python
from dictquerier import query_json, JsonPathError

try:
    result = query_json(data, "不存在的路径")
except JsonPathError as e:
    print(f"路径错误: {e}")
except SyntaxError as e:
    print(f"语法错误: {e}")
```

## 许可证

MIT许可证
