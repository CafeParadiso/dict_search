from .operators import Operator


class LoadOpsError(Exception):
    def __init__(self, existing_op: type, op_name, repeated_op: type, op_module):
        super().__init__(
            f"\nAn operator named '{op_name}' already exists.\n"
            f"Existing operator: {existing_op.__name__}\n"
            f"Repeated operator: {repeated_op.__name__}\n"
            f"Repeated operator found in '{op_module.__name__}'"
        )


class PreconditionError(Exception):
    def __init__(self):
        super().__init__("Provide a dict to perform the matching or select")


class SelectValueError(Exception):
    def __init__(self):
        super().__init__(f"Use operators or keys with a value of 0 or 1 in your select query")


class SelectMixedError(Exception):
    def __init__(self):
        super().__init__("Do not mix inclusion and exclusion in the same query")


class CustomOpsKeyError(Exception):
    def __init__(self, ops_str):
        super().__init__(
            f"Pass a 'str' as key a of your operator dict.\n" f"As an example, 'op' would be parsed to '{ops_str}op'"
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
            f"Remember to use the name of the operator withouth its operator string, 'op' not '{ops_str}op'\n"
        )


class OpsConfigKeyError(KeyError):
    def __init__(self, k, op_name, conf_key):
        super().__init__(
            f"\nYou provided an invalid configuration key, '{k}' for the operator '{op_name}' via '{conf_key}'.\n"
        )
