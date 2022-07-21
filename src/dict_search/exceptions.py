from . import constants


class PreconditionError(Exception):
    def __init__(self):
        super().__init__("Provide a dict to perform the matching or select")


class HighLevelOperatorIteratorError(TypeError):
    def __init__(self):
        super().__init__("The search value for a high level operator must be a list")


class MatchOperatorError(TypeError):
    def __init__(self, search_operator):
        super().__init__(
            f"Any match operator must be a dict like {{'$match_op': count(int): search_val}}, not:\n {search_operator}"
        )


class WhereOperatorError(TypeError):
    def __init__(self):
        super().__init__(
            "The search value for 'where' must be a list of two elements: [{array_match_condition}, {match_dict}]"
        )


class ArraySelectorFormatException(ValueError):
    def __init__(self, operator):
        super().__init__(f"Use a dict as '{operator}' operator to match")


class RangeSelectionOperatorError(ValueError):
    def __init__(self, operator):
        super().__init__(f"Use a 'rangestr' matchin any pattern in {constants.RANGE_PATTERN} not:\n '{operator}'")


class CompException(Exception):
    def __init__(self):
        super().__init__(
            "$comp must be either a list of keys to get a value and compare it or \n"
            "a list of keys and a comparison function with two args, x -> current value, y ->searched value\n"
            "-{'$comp': ['a']}"
            "-{'$comp': [['a'], lambda: x, y: x != y]}'"
        )
