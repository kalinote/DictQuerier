from dictquerier.executor.visitor import ASTVisitor
from dictquerier.script.manager import script_manager
from dictquerier.tokenizer.enum import Operator
from dictquerier.syntax_tree.node import *
from dictquerier.exceptions import UnknownOperator

class Evaluator(ASTVisitor):
    """
    执行器，用于执行AST节点
    """
    def __init__(self, data):
        self.data = data
        self.context = {}

    def query(self, ast_root: ASTNode):
        """查询入口方法"""
        # 标记当前是根查询
        self.context['is_root_query'] = True
        result = self.visit(ast_root)
        return result

    def visit_NameNode(self, node: NameNode):
        # 如果是根查询，从self.data中获取对应键的值
        if self.context.get('is_root_query', False):
            name = node.name
            # 取消根查询标记，避免后续节点也被当作根查询
            self.context['is_root_query'] = False
            
            # 如果是根级别的通配符，返回整个数据
            if getattr(node, '_is_root_wildcard', False):
                return self.data
                
            # 从数据中获取对应的值
            if isinstance(self.data, dict) and name in self.data:
                return self.data[name]
            return None
        
        if 'current_item' in self.context:
            raise NameError(f"名称 '{node.name}' 未定义，位于 {node.line} 行 {node.column} 列")
        
        # 非根查询，直接返回节点名称
        return node.name
        
    def visit_NumberNode(self, node: NumberNode):
        return node.value
        
    def visit_StringNode(self, node: StringNode):
        """
        访问字符串节点
        当在条件过滤上下文中时，尝试从当前项中获取对应键的值
        """
        value = node.value
        
        # 检查是否在条件过滤上下文中
        if 'current_item' in self.context:
            current_item = self.context['current_item']
            # 如果当前项是字典且包含该键
            if isinstance(current_item, dict) and value in current_item:
                return current_item[value]
        
        # 普通字符串
        return value

    def visit_VarRefNode(self, node: VarRefNode):
        # 变量操作时取消根查询标记
        self.context['is_root_query'] = False
        
        var_name = self.visit(node.name)
        
        # 首先从脚本管理器中获取
        var = script_manager.get(var_name)
        
        # 如果脚本管理器中没有获取到，则从数据中获取
        if not var:
            var = self.data.get(var_name)
        
        return var

    def visit_ScriptCallNode(self, node: ScriptCallNode):
        # 脚本操作时取消根查询标记
        self.context['is_root_query'] = False
        func_name = self.visit(node.name)
        module_path = ".".join([self.visit(module) for module in node.module])
        
        # 调用时会执行检查，这一步多余
        # if not script_manager.check_script(name=func_name, path=module_path):
        #     raise ValueError(f"未定义的脚本: {func_name}, 确保脚本在运行前已注册")
            
        # 求值所有参数
        args = [self.visit(arg) for arg in node.args]
        kwargs = {self.visit(key): self.visit(value) for key, value in node.kwargs.items()}

        # 调用脚本
        return script_manager.run(name=func_name, path=module_path, args=args, kwargs=kwargs)

    def visit_BinaryOpNode(self, node: BinaryOpNode):
        """
        处理二元操作符节点
        支持:
        1. 条件过滤 (>, <, ==, !=, >=, <=)
        2. 逻辑运算 (&&, ||)
        3. 四则运算 (+, -, *, /)
        """
        # 对于短路操作符，先评估左操作数
        left = self.visit(node.left)
        
        # 短路求值
        if node.op == Operator.LOGICAL_AND and not left:
            return False
        if node.op == Operator.LOGICAL_OR and left:
            return True
        
        # 对于非短路操作符或需要继续计算的短路操作符，计算右操作数
        right = self.visit(node.right)
        
        # 逻辑操作符
        if node.op == Operator.LOGICAL_AND:
            return left and right
        elif node.op == Operator.LOGICAL_OR:
            return left or right
        
        # 比较操作符
        elif node.op == Operator.EQUAL:
            return left == right
        elif node.op == Operator.NOT_EQUAL:
            return left != right
        elif node.op == Operator.GREATER_THAN:
            return left > right
        elif node.op == Operator.LESS_THAN:
            return left < right
        elif node.op == Operator.GREATER_EQUAL:
            return left >= right
        elif node.op == Operator.LESS_EQUAL:
            return left <= right
        
        # 算术操作符
        elif node.op == Operator.PLUS:
            return left + right
        elif node.op == Operator.MINUS:
            return left - right
        elif node.op == Operator.MULTIPLY:
            return left * right
        elif node.op == Operator.DIVIDE:
            # 防止除零错误
            if right == 0:
                raise ZeroDivisionError("除数不能为零")
            return left / right
        
        # 不支持的操作符
        else:
            raise UnknownOperator(f"不支持的操作符: {node.op}")

    def visit_KeyNode(self, node: KeyNode):
        obj = self.visit(node.obj)
        key = node.key
        
        if obj is None:
            return None
        
        # 处理通配符 obj.*
        if node.is_wildcard:
            # 列表对象
            if isinstance(obj, list):
                return obj
            
            # 字典
            if isinstance(obj, dict):
                return obj
                
            return None
            
        # 处理列表对象 - 对列表中的每个元素获取同名键
        if isinstance(obj, list):
            result = []
            for item in obj:
                if isinstance(item, dict) and key in item:
                    result.append(item[key])
                elif hasattr(item, key):
                    result.append(getattr(item, key))
            return result if result else None
            
        # 处理字典
        if isinstance(obj, dict):
            return obj.get(key)
            
        # 处理对象属性
        if hasattr(obj, key):
            return getattr(obj, key)
            
        return None
    
    def visit_IndexNode(self, node: IndexNode):
        obj = self.visit(node.obj)
        
        if obj is None:
            return None
        
        # 检查是否是通配符索引 (index 是 StringNode 且值为 *)
        if isinstance(node.index, StringNode) and node.index.value == '*':
            # 列表
            if isinstance(obj, list):
                return obj
            # 字典
            elif isinstance(obj, dict):
                return obj
            return None
        
        # 检查是否是条件过滤 (index 是 BinaryOpNode)
        if isinstance(obj, list) and isinstance(node.index, BinaryOpNode):
            result = []
            
            # 对列表中的每个元素应用条件
            for item in obj:
                # 保存旧上下文
                old_context = self.context.copy()
                
                # 设置当前项为上下文
                self.context['current_item'] = item
                
                try:
                    # 计算条件表达式
                    condition_result = self.visit(node.index)
                    
                    # 如果条件为真，将项添加到结果中
                    if condition_result:
                        result.append(item)
                finally:
                    # 恢复上下文
                    self.context = old_context
            
            return result
        
        # 处理字符串索引作为键访问的特殊情况，如obj["key"]
        if isinstance(node.index, StringNode):
            key = node.index.value
            # 对于字典，直接按键访问
            if isinstance(obj, dict):
                return obj.get(key)
            # 对于列表中的字典元素，获取指定键
            elif isinstance(obj, list):
                result = []
                for item in obj:
                    if isinstance(item, dict) and key in item:
                        result.append(item[key])
                    elif hasattr(item, key):
                        result.append(getattr(item, key))
                return result if result else None
            # 对于对象，尝试访问属性
            elif hasattr(obj, key):
                return getattr(obj, key)
            return None
        
        # 普通索引访问
        index = self.visit(node.index)
        
        # 处理列表或元组
        if isinstance(obj, (list, tuple)):
            if isinstance(index, int) and 0 <= index < len(obj):
                return obj[index]
            return None
        
        # 处理字典
        if isinstance(obj, dict):
            return obj.get(index)
        
        return None
    
    def visit_SliceNode(self, node: SliceNode):
        obj = self.visit(node.obj)
        
        if obj is None:
            return None
        
        # 检查切片值是否合法
        start = self.visit(node.start) if node.start else None
        end = self.visit(node.end) if node.end else None
        step = self.visit(node.step) if node.step else None
        
        if start and not isinstance(start, int):
            raise ValueError("切片起始值必须为整数")
        if end and not isinstance(end, int):
            raise ValueError("切片结束值必须为整数")
        if step and not isinstance(step, int):
            raise ValueError("切片步长必须为整数")
        if step == 0:
            raise ValueError("切片步长不能为0")
        
        # 暂定，后续可能增加一些特殊切片处理，比如numpy中的多维切片
        return obj[start:end:step]
    