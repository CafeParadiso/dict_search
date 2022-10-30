from ast import ClassDef as _ast_ClassDef
from ast import parse as _ast_parse
from inspect import getsource as _getsource
from types import ModuleType as _ModuleType

from .bases import ArrayOperator, ArraySelector, HighLevelOperator, LowLevelOperator, Operator

ALL_OPERATOR_TYPES = [LowLevelOperator, HighLevelOperator, ArrayOperator, ArraySelector, Operator]


def get_operators(module: _ModuleType) -> list[..., type]:
    ops = []
    for op_name in [node.name for node in _ast_parse(_getsource(module)).body if isinstance(node, _ast_ClassDef)]:
        op_class = getattr(module, op_name)
        if not issubclass(op_class, Operator):
            raise Exception(f"All class definitions in the module should be a subclass of '{Operator}'")
        ops.append(op_class)
    return ops
