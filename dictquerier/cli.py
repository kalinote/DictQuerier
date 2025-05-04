"""
命令行接口模块
"""
import argparse
import json
import sys
from typing import Any, Dict, List

from .core import query_json
from .exceptions import PathError

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="dictquerier - 一个灵活的JSON路径查询工具")
    parser.add_argument("-f", "--file", help="要查询的JSON文件路径")
    parser.add_argument("-p", "--path", required=True, help="查询路径表达式")
    parser.add_argument("-i", "--input", help="直接输入的JSON字符串，与-f互斥")
    parser.add_argument("-o", "--output", help="输出文件路径，默认为标准输出")
    parser.add_argument("-c", "--compact", action="store_true", help="输出紧凑的JSON格式")
    
    return parser.parse_args()

def main():
    """主入口函数"""
    args = parse_args()
    
    # 获取输入数据
    data = None
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"错误: 找不到文件 '{args.file}'", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"错误: 文件 '{args.file}' 不是有效的JSON格式", file=sys.stderr)
            sys.exit(1)
    elif args.input:
        try:
            data = json.loads(args.input)
        except json.JSONDecodeError:
            print("错误: 输入的字符串不是有效的JSON格式", file=sys.stderr)
            sys.exit(1)
    else:
        print("错误: 必须提供JSON数据（通过-f或-i参数）", file=sys.stderr)
        sys.exit(1)
    
    # 执行查询
    try:
        result = query_json(data, args.path)
        
        # 输出结果
        indent = None if args.compact else 2
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=indent)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=indent))
            
    except PathError as e:
        print(f"查询路径错误: {e}", file=sys.stderr)
        sys.exit(1)
    except SyntaxError as e:
        print(f"查询语法错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 