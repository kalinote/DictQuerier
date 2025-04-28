"""
操作符模块初始化文件
导入所有操作符子模块，确保注册代码被执行
"""
# 导入基础模块
from . import base
from . import enum
from . import register

# 导入操作符处理模块（这些模块中包含注册代码）
from . import compare
from . import logical
