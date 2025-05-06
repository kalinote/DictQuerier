# DictQuerier

基于路径的Python字典数据查询工具，支持复杂的路径表达式、条件筛选、变量引用和脚本调用功能。

> [!WARNING]
> 
> 主要用于研究学习，暂时还不兼容 JSON Path 语法，主要是写这个模块的时候我还不知道 JSON Path 这个东西...
> 
> 后续"可能会"逐步增加对 JSON Path 的兼容，但优先级不高。如果有类似的开发需求，请使用标准的 JSON Path

## 特性

- 支持条件表达式过滤（==, !=, >, <, >=, <=）
- 支持逻辑运算符（&&, ||）
- 支持算术运算符（+, -, *, /）
- 支持通配符（*）和切片操作（[start:end:step]）
- 支持变量引用（$varname）
- 支持脚本调用（@function(args)）
- 支持模块路径调用（@module.function(args)）
- 支持任意层级的嵌套数据访问
- 完善的错误处理机制
- 详细的类型标注

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
result3 = query_json(data, "*.users[0].name")  # 返回: "张三"（根级别通配符）

# 条件表达式查询
result4 = query_json(data, "users['id'==2].name")  # 返回: ["李四"]
result5 = query_json(data, "users['id'>1].name")  # 返回: ["李四", "王五"]

# 复杂条件查询
result6 = query_json(data, "users['id'==1||'id'==3].scores")  # 返回: [[80, 90, 85], [95, 88, 75]]
result7 = query_json(data, "users['id'>1 && 'scores'[0]>=70].name")  # 返回: ["李四", "王五"]

# 切片操作
result8 = query_json(data, "users[1:3].name")  # 返回: ["李四", "王五"]
result9 = query_json(data, "users[0].scores[::2]")  # 返回: [80, 85]（跳步为2）

# 字符串字面量和字典键访问
result10 = query_json(data, "users[0]['name']")  # 返回: "张三"

# 算术运算
from dictquerier.script.manager import script_manager
script_manager.define("factor", 10)
result11 = query_json(data, "users[0].scores[0] * $factor")  # 返回: 800
```

### 变量和脚本

```python
from dictquerier import query_json
from dictquerier.script.manager import script_manager

# 注册脚本函数
@script_manager.register()
def average(numbers):
    return sum(numbers) / len(numbers)

# 定义变量
script_manager.define("threshold", 85)

data = {
    "users": [
        {"id": 1, "name": "张三", "scores": [80, 90, 85]},
        {"id": 2, "name": "李四", "scores": [70, 85, 92]},
        {"id": 3, "name": "王五", "scores": [95, 88, 75]}
    ]
}

# 使用脚本函数
avg_score = query_json(data, "@average(users[0].scores)")  # 返回: 85.0

# 使用变量引用
high_scores = query_json(data, "users[@average('scores') > $threshold].name")  # 返回: ["李四"]
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

## 语法说明

### 基本语法

- `.` - 子元素访问（如 `users.name`）
- `[数字]` - 索引访问（如 `users[0]`）
- `['键名']` - 字符串键访问（如 `users['name']`）
- `[*]` - 通配符，表示所有元素
- `.*` - 通配符，同上但使用点语法
- `[start:end:step]` - 切片操作（如 `users[1:3]`, `scores[::-1]`）
- `['键名' 操作符 值]` - 条件过滤（如 `users['id'>2]`）

### 操作符

- 比较操作符: `==`, `!=`, `<`, `>`, `<=`, `>=`
- 逻辑操作符: `&&`, `||`
- 算术操作符: `+`, `-`, `*`, `/`

### 变量和脚本

- `$变量名` - 变量引用（如 `$threshold`）
- `@函数名(参数)` - 脚本调用（如 `@average(scores)`）
- `@模块.函数名(参数)` - 带模块路径的脚本调用

## 高级用法

### 嵌套调用

```python
# 在表达式中嵌套使用脚本调用
result = query_json(data, "users[@filter_active(*)].addresses[@primary(*)]")
```

### 组合条件

```python
# 使用复杂逻辑条件
result = query_json(data, "users[('age'>18 && 'active'==true) || 'role'=='admin']")
```

### 错误处理

```python
from dictquerier import query_json
from dictquerier.exceptions import UnknownOperator

try:
    result = query_json(data, "users[name~~'张']")  # 使用未定义的操作符
except UnknownOperator as e:
    print(f"操作符错误: {e}")
except SyntaxError as e:
    print(f"语法错误: {e}")
except Exception as e:
    print(f"查询错误: {e}")

# 静默错误处理
result = query_json(data, "不存在的路径", no_path_exception=True)  # 返回 []
```

## 实现细节

DictQuerier 使用递归下降解析器实现语法分析，并使用访问者模式遍历抽象语法树执行查询。整个执行过程包括：

1. 词法分析：将查询字符串转换为标记流
2. 语法分析：将标记流解析为抽象语法树
3. 执行：遍历语法树并执行相应操作

## 许可证

MIT许可证
