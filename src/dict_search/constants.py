import re


LOP_CONF_EXC = "exc"
LOP_CONF_EXC_VAL = "exc_val"
LOP_CONF_ALL_TYPE = "allowed"
LOP_CONF_IG_TYPE = "ignored"
LOP_CONF_KEYS = [LOP_CONF_EXC, LOP_CONF_EXC_VAL, LOP_CONF_ALL_TYPE, LOP_CONF_IG_TYPE]

RANGE_PATTERN = re.compile(
    r"^(-?\d+)::?$|"
    r"^:(-?\d+):?$|"
    r"^::(-?\d+)$|"
    r"^(-?\d+):(-?\d+):?$|"
    r"^(-?\d+)::(-?\d+)$|"
    r"^:(-?\d+):(-?\d+)$|"
    r"^(-?\d+):(-?\d+):(-?\d+)$|"
    r"^:$"
)

__all__ = [
    "LOP_CONF_EXC", "LOP_CONF_EXC_VAL", "LOP_CONF_ALL_TYPE", "LOP_CONF_IG_TYPE", "LOP_CONF_KEYS", "RANGE_PATTERN"
]
