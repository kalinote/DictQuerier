
from dictquerier.expression.base import BaseExpression


class ScriptExpression(BaseExpression):
    def __init__(self, name: str, args: list, kwargs: dict):
        super().__init__(value=name, args=args, kwargs=kwargs)

    def operate(self, data):
        raise NotImplementedError(f"脚本运算暂未实现: {self.name}")

    def get_expression(self):
        return f"{self.value}({', '.join(map(str, self.args))}, {', '.join([f'{k}={v}' for k, v in self.kwargs.items()])})"
