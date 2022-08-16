from . import constants


class PreconditionError(SyntaxError):
    def __init__(self):
        super().__init__("Provide a dict to perform the matching or select")


class HighLevelOperatorIteratorError(SyntaxError):
    def __init__(self, container_type):
        super().__init__(f"The search value for a high level operator must be a non empty {container_type}")


class MatchOperatorError(SyntaxError):
    def __init__(self, search_operator):
        super().__init__(
            f"Any match operator must be a dict like {{'$match_op': count(int): search_val}}, not:\n {search_operator}"
        )


class WhereOperatorError(SyntaxError):
    def __init__(self):
        super().__init__(
            "The search value for 'where' must be a list of two elements: [{array_match_condition}, {match_dict}]"
        )


class ArraySelectorFormatException(SyntaxError):
    def __init__(self, operator):
        super().__init__(f"Use a dict as '{operator}' operator to match")


class RangeSelectionOperatorError(SyntaxError):
    def __init__(self, operator):
        super().__init__(f"Use a 'rangestr' matching any pattern in {constants.RANGE_PATTERN} not:\n '{operator}'")


class CompException(SyntaxError):
    def __init__(self):
        super().__init__(
            "\n"
            "$comp must be either a list of keys to get a value and compare it or \n"
            "a list of keys and a comparison function with two args, x -> current value, y ->searched value\n"
            "-{'$comp': ['a']}"
            "-{'$comp': [['a'], lambda: x, y: x != y]}'"
        )


class IndexOperatorError(SyntaxError):
    def __init__(self):
        super().__init__(
            "\n"
            "$index must be either a dict:\n"
            "- {index(int): val(any or dict)}\n"
            "or a list:\n"
            "- [[index(int)], val(any or dict)]"
        )
