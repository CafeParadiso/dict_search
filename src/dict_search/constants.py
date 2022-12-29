import sys as _sys

from .operators.operators import (
    low_level_operators as _low_level_operators,
    high_level_operators as _high_level_operators,
    array_operators as _array_operators,
    array_selectors as _array_selectors,
    count_operators as _count_operators,
    match_operators as _match_operators,
)
from .operators import get_operators as _get_operators


def __set_operators__():
    for __module in [
        _low_level_operators,
        _high_level_operators,
        _array_operators,
        _array_selectors,
        _match_operators,
        _count_operators,
    ]:
        for __op_class in _get_operators(__module):
            setattr(_sys.modules[__name__], f"op__{__op_class.name}".upper(), __op_class.name)


__set_operators__()
