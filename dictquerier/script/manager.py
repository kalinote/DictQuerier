import importlib
import functools
from typing import Any, Callable, Tuple, Optional

from dictquerier.exceptions import UnknowScript

class ScriptManager:
    def __init__(self):
        self.scripts = {}
        self.variables = {}
        
        # 缓存数据
        self._module_cache = {}
        self._function_cache = {}
        
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
    
    def unregister(self, name: str) -> bool:
        """
        卸载已注册的脚本
        
        Args:
            name (str): 要卸载的脚本名称
        Returns:
            bool: 卸载是否成功
        """
        if name in self.scripts:
            # 从scripts字典中移除
            del self.scripts[name]
            
            # 清除相关缓存
            self.clear_specific_cache(name)
            
            return True
        return False
    
    def _get_cache_key(self, name: str, path: str = None) -> str:
        """生成缓存键"""
        return f"{path}:{name}" if path else name

    def _record_call(self):
        """记录调用统计"""
        self._stats['total_calls'] += 1

    def _record_hit(self):
        """记录缓存命中"""
        self._stats['hits'] += 1

    def _record_miss(self):
        """记录缓存未命中"""
        self._stats['misses'] += 1

    def check_script(self, name: str, path: str = None) -> bool:
        """
        检查脚本是否存在或可调用

        Args:
            name (str): 脚本名
            path (str): 模块路径，可选
        Returns:
            bool: 是否存在或可调用
        """
        # 直接使用_get_function的结果
        _, is_callable = self._get_function(name, path)
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
        self._record_call()
        
        cache_key = self._get_cache_key(name, path)
        if cache_key in self._function_cache:
            self._record_hit()
            return self._function_cache[cache_key]
        
        self._record_miss()
        result = (None, False)
        
        # 已注册的脚本
        if name in self.scripts:
            result = (self.scripts[name], True)
            
        # 变量属性访问
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
        
        # 多级模块导入和属性访问
        if result == (None, False):  # 如果前面的尝试都失败了
            try:
                if path:
                    # 处理多级路径
                    if '.' in path:
                        try:
                            path_parts = path.split('.')
                            module = self._import_module(path_parts[0])
                            obj = module
                            
                            for part in path_parts[1:]:
                                obj = getattr(obj, part)
                                
                            if hasattr(obj, name):
                                func = getattr(obj, name)
                                if callable(func):
                                    result = (func, True)
                        except (ImportError, AttributeError, ValueError):
                            pass
                    else:
                        # 单级路径，直接导入模块
                        try:
                            module = self._import_module(path)
                            if hasattr(module, name):
                                func = getattr(module, name)
                                if callable(func):
                                    result = (func, True)
                        except (ImportError, AttributeError, ValueError):
                            pass
                else:
                    # 处理name是多级路径的情况
                    full_path = name
                    parts = full_path.split('.')
                    if len(parts) > 1:
                        module_path = parts[0]
                        attr_chain = parts[1:]
                        
                        try:
                            module = self._import_module(module_path)
                            obj = module
                            
                            for attr in attr_chain:
                                obj = getattr(obj, attr)
                            
                            result = (obj, callable(obj))
                        except (ImportError, AttributeError, ValueError):
                            for i in range(1, len(parts)):
                                try:
                                    potential_module = '.'.join(parts[:i])
                                    potential_attrs = parts[i:]
                                    
                                    module = self._import_module(potential_module)
                                    obj = module
                                    
                                    for attr in potential_attrs:
                                        obj = getattr(obj, attr)
                                    
                                    if callable(obj):
                                        result = (obj, True)
                                        break
                                except (ImportError, AttributeError, ValueError):
                                    continue
            except Exception:
                pass
        
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
            raise UnknowScript(f"'{path}.{name}' 不存在或不是可调用对象")
        elif '.' in name:
            raise UnknowScript(f"'{name}' 不存在或不是可调用对象")
        else:
            raise UnknowScript(f"脚本 '{name}' 未找到或不可调用")

    def define(self, var_name, var_value):
        self.variables[var_name] = var_value
        
    def get(self, var_name):
        return self.variables.get(var_name)

    def clear_cache(self, cache_type=None):
        """
        清理缓存
        
        Args:
            cache_type (str, optional): 要清理的缓存类型，可选值：'module', 'function' 或 None(清理所有)
        """
        if cache_type is None or cache_type == 'module':
            self._module_cache.clear()
            
        if cache_type is None or cache_type == 'function':
            self._function_cache.clear()
            
    def clear_specific_cache(self, name: str, path: str = None):
        """
        清理特定脚本的缓存
        
        Args:
            name (str): 脚本名
            path (str, optional): 模块路径
        """
        cache_key = self._get_cache_key(name, path)
        
        if cache_key in self._function_cache:
            del self._function_cache[cache_key]
            
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
                'function': len(self._function_cache)
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
            self._record_hit()
            return self._module_cache[module_path]
        
        try:
            self._record_miss()
            module = importlib.import_module(module_path)
            self._module_cache[module_path] = module
            return module
        except ImportError as e:
            raise ValueError(f"无法导入模块 '{module_path}': {e}")

script_manager = ScriptManager()
