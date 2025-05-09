import importlib
import functools
from typing import Any, Callable, Tuple, Optional

class ScriptManager:
    def __init__(self):
        self.scripts = {}
        self.variables = {}
        
        # 缓存数据
        self._module_cache = {}
        self._function_cache = {}
        self._check_cache = {}
        
        # 调用状态统计
        self._stats = {
            'hits': 0,
            'misses': 0,
            'total_calls': 0,
        }

    def register(self, name: str = None):
        """
        注册脚本

        Args:
            name (str, optional): 自定义脚本调用名，可选
        Returns:
        """
        def decorator(func):
            key = name or func.__name__
            self.scripts[key] = func
            return func
        return decorator

    def check_script(self, name: str, path: str = None) -> bool:
        """
        检查脚本是否存在或可调用

        Args:
            name (str): 脚本名
            path (str): 模块路径，可选
        Returns:
            bool: 是否存在或可调用
        """
        self._stats['total_calls'] += 1
        
        # 尝试从缓存中获取结果
        cache_key = f"{path}:{name}" if path else name
        if cache_key in self._check_cache:
            self._stats['hits'] += 1
            return self._check_cache[cache_key]
        
        # 缓存未命中
        self._stats['misses'] += 1
        
        _, is_callable = self._get_function(name, path)
        self._check_cache[cache_key] = is_callable
        
        return is_callable
    
    def _get_function(self, name: str, path: str = None) -> Tuple[Optional[Callable], bool]:
        """
        获取脚本并缓存结果
        
        Args:
            name: 脚本名
            path: 模块路径，可选
        Returns:
            (脚本对象, 是否可调用)
        """
        self._stats['total_calls'] += 1
        
        # 尝试从缓存中获取结果
        cache_key = f"{path}:{name}" if path else name
        if cache_key in self._function_cache:
            self._stats['hits'] += 1
            return self._function_cache[cache_key]
        
        # 缓存未命中
        self._stats['misses'] += 1
        result = (None, False)
        
        if name in self.scripts:
            result = (self.scripts[name], True)
            
        elif '.' in name and not path:
            var_parts = name.split('.')
            var_name = var_parts[0]
            if var_name in self.variables:
                try:
                    obj = self.variables[var_name]
                    for part in var_parts[1:]:
                        obj = getattr(obj, part)
                    result = (obj, callable(obj))
                except (AttributeError, TypeError):
                    pass
                    
        # 检查全局脚本
        elif not path:
            import __main__
            main_globals = vars(__main__)
            
            if name in main_globals and callable(main_globals[name]):
                result = (main_globals[name], True)
            else:
                import builtins
                if hasattr(builtins, name):
                    builtin_obj = getattr(builtins, name)
                    if callable(builtin_obj):
                        result = (builtin_obj, True)
                
        # 带path参数
        elif path:
            try:
                parts = path.split('.')
                if len(parts) > 1:
                    try:
                        base_module = self._import_module(parts[0])
                        obj = base_module
                        
                        for part in parts[1:]:
                            obj = getattr(obj, part)
                        
                        func = getattr(obj, name)
                        result = (func, callable(func))
                    except (ValueError, AttributeError):
                        pass
                else:
                    try:
                        module = self._import_module(path)
                        func = getattr(module, name)
                        result = (func, callable(func))
                    except (ValueError, AttributeError):
                        pass
            except Exception:
                pass
        
        # 脚本解析或多级解析
        else:
            full_path = name
            parts = full_path.split('.')
            if len(parts) > 1:
                for i in range(len(parts) - 1, 0, -1):
                    module_path = '.'.join(parts[:i])
                    attr_chain = parts[i:]
                    try:
                        module = self._import_module(module_path)
                        obj = module
                        for attr in attr_chain:
                            obj = getattr(obj, attr)
                        if callable(obj):
                            result = (obj, True)
                            break
                    except (ValueError, AttributeError):
                        continue
        
        # 保存到缓存
        self._function_cache[cache_key] = result
        return result
            
    def run(self, name: str, path: str = None, args=None, kwargs=None):
        """
        调用脚本

        Args:
            name (str): 脚本名
            path (str): 模块路径，可选
            args: 位置参数列表
            kwargs: 关键字参数字典
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        
        # 通过缓存获取脚本
        func, is_callable = self._get_function(name, path)
        
        if func and is_callable:
            return func(*args, **kwargs)
            
        if path:
            raise ValueError(f"'{path}.{name}' 不存在或不是可调用对象")
        elif '.' in name:
            raise ValueError(f"'{name}' 不存在或不是可调用对象")
        else:
            raise ValueError(f"脚本 '{name}' 未找到或不可调用")

    def define(self, var_name, var_value):
        self.variables[var_name] = var_value
        
    def get(self, var_name):
        return self.variables.get(var_name)

    def clear_cache(self, cache_type=None):
        """
        清理缓存
        
        Args:
            cache_type (str, optional): 要清理的缓存类型，可选值：'module', 'function', 'check' 或 None(清理所有)
        """
        if cache_type is None or cache_type == 'module':
            self._module_cache.clear()
            
        if cache_type is None or cache_type == 'function':
            self._function_cache.clear()
            
        if cache_type is None or cache_type == 'check':
            self._check_cache.clear()
            
    def clear_specific_cache(self, name: str, path: str = None):
        """
        清理特定脚本的缓存
        
        Args:
            name (str): 脚本名
            path (str, optional): 模块路径
        """
        cache_key = f"{path}:{name}" if path else name
        
        if cache_key in self._function_cache:
            del self._function_cache[cache_key]
            
        if cache_key in self._check_cache:
            del self._check_cache[cache_key]
            
        # 如果有path，尝试清理模块缓存
        if path:
            parts = path.split('.')
            module_path = parts[0]  # 只清理顶级模块
            
            if module_path in self._module_cache:
                del self._module_cache[module_path]

    def get_stats(self):
        """
        获取缓存统计信息
        
        Returns:
            dict: 包含缓存统计数据的字典
        """
        stats = {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'total_calls': self._stats['total_calls'],
            'cache_size': {
                'module': len(self._module_cache),
                'function': len(self._function_cache),
                'check': len(self._check_cache)
            }
        }
        
        if stats['total_calls'] > 0:
            stats['hit_ratio'] = stats['hits'] / stats['total_calls']
        else:
            stats['hit_ratio'] = 0
            
        return stats
        
    def reset_stats(self):
        """重置统计计数器"""
        self._stats = {
            'hits': 0,
            'misses': 0,
            'total_calls': 0,
        }

    def _import_module(self, module_path: str) -> Any:
        """
        导入模块并缓存结果
        
        Args:
            module_path: 模块路径
        Returns:
            导入的模块
        """
        if module_path in self._module_cache:
            # 命中缓存
            self._stats['hits'] += 1
            return self._module_cache[module_path]
        
        try:
            self._stats['misses'] += 1
            module = importlib.import_module(module_path)
            self._module_cache[module_path] = module
            return module
        except ImportError as e:
            raise ValueError(f"无法导入模块 '{module_path}': {e}")

script_manager = ScriptManager()
