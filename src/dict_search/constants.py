import sys as _sys

from .operators import low_level_operators as _low_level_operators
from .operators import high_level_operators as _high_level_operators
from .operators import array_operators as _array_operators
from .operators import array_selectors as _array_selectors
from .operators import get_operators as _get_operators


LOP_CONF_EXC = "expected_exc"
LOP_CONF_ALL_TYPE = "allowed_types"
LOP_CONF_IG_TYPE = "ignored_types"
LOP_CONF_DEF_RET = "default_return"
LOP_CONF_KEYS = [LOP_CONF_EXC, LOP_CONF_ALL_TYPE, LOP_CONF_IG_TYPE, LOP_CONF_DEF_RET]


def __set_operators__():
    for __module in [_low_level_operators, _high_level_operators, _array_operators, _array_selectors]:
        for __op_class in _get_operators(__module):
            setattr(_sys.modules[__name__], f"op_{__op_class.name}".upper(), __op_class.name)


__set_operators__()
