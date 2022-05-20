class PreconditionError(Exception):
    def __init__(self):
        super().__init__("Provide a dict to perform the matching and select")


class HighLevelOperatorIteratorError(TypeError):
    def __init__(self):
        super().__init__("The search value for a high level operator must be a container (but not a dict)")


class WhereOperatorError(TypeError):
    def __init__(self):
        super().__init__(
            "The search value for 'where' must be a container of two elements: [{array_match_condition}, {match_dict}]"
        )
