"""
基本使用示例
"""
import json
from dictquerier import query_json, JsonPathError

def main():
    """主函数"""
    # 示例数据
    data = {
        "users": [
            {"id": 1, "name": "张三", "scores": [80, 90, 85], "active": True},
            {"id": 2, "name": "李四", "scores": [70, 85, 92], "active": False},
            {"id": 3, "name": "王五", "scores": [95, 88, 75], "active": True}
        ],
        "settings": {
            "pagination": {"page": 1, "size": 10},
            "filters": ["name", "id", "active"]
        }
    }
    
    # 基本查询示例
    examples = [
        ("users[0].name", "基本路径访问"),
        ("users[*].name", "通配符访问所有用户名"),
        ("users['id'==2].name", "条件过滤 - 查找ID为2的用户名"),
        ("users['id'>1].name", "比较操作 - 查找ID大于1的用户名"),
        ("users['active'==true].name", "布尔值条件 - 查找活跃用户的名字"),
        ("users['id'==1||'id'==3].name", "逻辑OR - 查找ID为1或3的用户名"),
        ("users['id'==1&&'active'==true].name", "逻辑AND - 查找ID为1且活跃的用户名"),
        ("users[0:2].name", "切片操作 - 前两个用户的名字"),
        ("users[0].scores[::2]", "步长切片 - 第一个用户的偶数位置分数"),
        ("settings.pagination.page", "嵌套对象访问"),
        ("settings.filters[*]", "访问数组中的所有元素")
    ]
    
    # 执行示例并打印结果
    for path, description in examples:
        try:
            result = query_json(data, path)
            print(f"\n示例: {description}")
            print(f"路径: {path}")
            print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        except (JsonPathError, SyntaxError) as e:
            print(f"\n示例: {description} - 发生错误")
            print(f"路径: {path}")
            print(f"错误: {e}")
    
    # 错误处理示例
    error_examples = [
        ("users[10].name", "索引越界"),
        ("users[id==1].name", "无引号的键名"),
        ("users.not_exists", "不存在的属性"),
        ("users[0].scores[2:5:0]", "切片步长为0（非法）")
    ]
    
    print("\n\n错误处理示例:")
    for path, description in error_examples:
        try:
            result = query_json(data, path, no_path_exception=False)
            print(f"\n示例: {description}")
            print(f"路径: {path}")
            print(f"结果 (未预期): {json.dumps(result, ensure_ascii=False)}")
        except Exception as e:
            print(f"\n示例: {description}")
            print(f"路径: {path}")
            print(f"错误 (预期): {type(e).__name__}: {e}")

if __name__ == "__main__":
    main() 