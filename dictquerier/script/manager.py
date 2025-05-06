import importlib

class ScriptManager:
    def __init__(self):
        self.scripts = {}
        self.variables = {}

    def register(self, name: str = None):
        def decorator(func):
            key = name or func.__name__
            self.scripts[key] = func
            return func
        return decorator

    def check_script(self, name: str, path: str = None) -> bool:
        """
        检查脚本是否存在或可调用

        Args:
            name (str): 函数名
            path (str): 模块路径，可选
        Returns:
            bool: 是否存在或可调用
        """
        # 检查已注册脚本
        if name in self.scripts:
            return True

        # 检查模块路径
        if path:
            try:
                module = importlib.import_module(path)
                obj = getattr(module, name)
                return callable(obj)
            except (ImportError, AttributeError):
                return False

        # 检查函数
        obj = globals().get(name)
        if callable(obj):
            return True

        # 多级解析，适用于name包含模块路径的情况
        parts = name.split('.')
        if len(parts) > 1:
            # 从最右侧拆分模块名
            for i in range(len(parts) - 1, 0, -1):
                module_path = '.'.join(parts[:i])
                attr_chain = parts[i:]
                try:
                    module = importlib.import_module(module_path)
                except ImportError:
                    continue
                try:
                    obj = module
                    for attr in attr_chain:
                        obj = getattr(obj, attr)
                    return callable(obj)
                except AttributeError:
                    return False

        return False

    def run(self, name: str, path: str = None, args=None, kwargs=None):
        """
        调用函数

        Args:
            name (str): 函数名
            path (str): 模块路径，可选
        """
        # 已注册脚本
        if name in self.scripts:
            return self.scripts[name](*args, **kwargs)

        # 带path参数
        if path:
            try:
                module = importlib.import_module(path)
                func = getattr(module, name)
            except (ImportError, AttributeError) as e:
                raise ValueError(f"无法导入或获取 {path}.{name}: {e}")
            if callable(func):
                return func(*args, **kwargs)
            else:
                raise ValueError(f"'{path}.{name}' 不是可调用对象")

        # 函数解析或多级解析
        full_path = name
        parts = full_path.split('.')
        if len(parts) < 2:
            raise ValueError(f"脚本 {name} 未注册，且不是有效的模块路径调用")

        for i in range(len(parts) - 1, 0, -1):
            module_path = '.'.join(parts[:i])
            attr_chain = parts[i:]
            try:
                module = importlib.import_module(module_path)
            except ImportError:
                continue

            try:
                obj = module
                for attr in attr_chain:
                    obj = getattr(obj, attr)
            except AttributeError:
                raise ValueError(f"模块 '{module_path}' 中不存在属性 '{'.'.join(attr_chain)}'")

            if callable(obj):
                return obj(*args, **kwargs)
            else:
                raise ValueError(f"'{full_path}' 解析结果不可调用")

        raise ValueError(f"脚本 '{full_path}' 未找到或不可调用")

    def define(self, var_name, var_value):
        self.variables[var_name] = var_value
        
    def get(self, var_name):
        return self.variables.get(var_name)

script_manager = ScriptManager()
