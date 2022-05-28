class PreconditionError(Exception):
    def __init__(self):
        super().__init__("Provide a dict to perform the matching or select")


class HighLevelOperatorIteratorError(TypeError):
    def __init__(self):
        super().__init__("The search value for a high level operator must be a container (but not a dict)")


class WhereOperatorError(TypeError):
    def __init__(self):
        super().__init__(
            "The search value for 'where' must be a container of two elements: [{array_match_condition}, {match_dict}]"
        )


class ArraySelectorFormatException(ValueError):
    def __init__(self, operator):
        super().__init__(f"Use a dict as '{operator}' operator to match")
