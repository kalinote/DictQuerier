class ASTVisitor:
    """AST访问者基类"""
    
    def generic_visit(self, node):
        """默认访问方法"""
        raise NotImplementedError(f"未实现节点类型 {node.__class__.__name__} 的访问方法")
        
    def visit(self, node):
        """访问节点入口方法"""
        return node.accept(self)
    