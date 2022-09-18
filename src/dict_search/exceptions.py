from .constants import LOP_CONF_KEYS, LOP_CONF_EXC
from .operators import ALL_OPERATOR_TYPES, Operator


class PreconditionError(Exception):
    def __init__(self):
        super().__init__("Provide a dict to perform the matching or select")


class CustomOpsKeyError(Exception):
    def __init__(self, ops_str):
        super().__init__(
                    f"Pass a 'str' as key a of your operator dict.\n"
                    f"As an example, 'op' would be parsed to '{ops_str}op'"
                )


class CustomOpsExistingKey(Exception):
    def __init__(self, custom_op):
        super().__init__(f"Your custom operator '{custom_op}' collides with an existing one")


class CustomOpsValueError(Exception):
    def __init__(self):
        super().__init__(f"All custom operators should be a subclass of '{Operator.__name__}'")


class OpsConfigNonExistingKey(Exception):
    def __init__(self, op_name, ops_str):
        super().__init__(
            f"You provided the name for an operator that does not exist, '{op_name}'.\n"
            f"Use the name of the operator withouth its operator string:\n"
            f"{{'op': {{{LOP_CONF_EXC}: TypeError}}}} not {{'{ops_str}op': {{{LOP_CONF_EXC}: TypeError}}}}"
        )


class OpsConfigKeyError(Exception):
    def __init__(self):
        super().__init__(
            f"Use as config keys the name of existing operators or operator types in {ALL_OPERATOR_TYPES}:\n"
            f"{{{Operator}: {{{LOP_CONF_EXC}: TypeError}}}}"
        )


class OpsConfigValueError(Exception):
    def __init__(self):
        super().__init__(f"Configure your operator with a dict containing any of these keys\n:{LOP_CONF_KEYS}")
