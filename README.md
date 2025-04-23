# JsonQuerier

基于路径的Python字典或Json数据查询工具，支持复杂的路径表达式、条件筛选和数据提取。

## 特性

- 支持类似JSONPath的简洁语法
- 支持条件表达式过滤
- 支持通配符和切片操作
- 全面的错误处理
- 完善的类型标注
- 提供命令行工具

## 安装

```bash
pip install JsonQuerier
```

## 快速开始

### Python API

```python
from jsonquerier import query_json

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
jsonquerier -f data.json -p "users[*].name"

# 直接使用JSON字符串
jsonquerier -i '{"users":[{"id":1,"name":"张三"}]}' -p "users[0].name"

# 保存结果到文件
jsonquerier -f data.json -p "users['id'>1]" -o result.json

# 使用紧凑输出格式
jsonquerier -f data.json -p "users[*].name" -c
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

## 错误处理

```python
from jsonquerier import query_json, JsonPathError

try:
    result = query_json(data, "不存在的路径")
except JsonPathError as e:
    print(f"路径错误: {e}")
except SyntaxError as e:
    print(f"语法错误: {e}")
```

## 许可证

MIT许可证
