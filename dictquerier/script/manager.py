import functools

class ScriptManager:
    def __init__(self):
        self.scripts = {}
        self.variables = {}

    def register(
        self, 
        name: str = None
        ):
        def decorator(func):
            self.scripts[name] = func
            return func
        return decorator
    
    def check_script(self, name):
        return name in self.scripts
    
    def run(self, name, *args, **kwargs):
        if name not in self.scripts:
            raise ValueError(f"脚本 {name} 未注册")
        return self.scripts[name](*args, **kwargs)
    
    def define(self, var_name, var_value):
        self.variables[var_name] = var_value
        
    def get(self, var_name):
        return self.variables.get(var_name)

script_manager = ScriptManager()
