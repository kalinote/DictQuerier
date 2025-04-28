import functools

class ScriptManager:
    def __init__(self):
        self.scripts = {}

    def register(
        self, 
        name: str = None
        ):
        def decorator(func):
            self.scripts[name] = func
            return func
        return decorator
    
    def run(self, name, *args, **kwargs):
        if name not in self.scripts:
            raise ValueError(f"脚本 {name} 未注册")
        return self.scripts[name](*args, **kwargs)

script_manager = ScriptManager()
