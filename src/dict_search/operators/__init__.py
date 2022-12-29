from inspect import isclass, getmembers, isabstract
from types import ModuleType as _ModuleType

from .bases import ArrayOperator, ArraySelector, HighLevelOperator, LowLevelOperator, Operator

ALL_OPERATOR_TYPES = [LowLevelOperator, HighLevelOperator, ArrayOperator, ArraySelector, Operator]


def get_operators(module: _ModuleType) -> list[..., type]:
    classes = getmembers(module, isclass)
    return list(
        map(
            lambda x: x[1],
            filter(lambda x: isinstance(x[1], type) and issubclass(x[1], Operator) and not isabstract(x[1]), classes),
        )
    )
