class PreconditionDataError(Exception):
    def __init__(self, data):
        super().__init__(f"\nData must be an iterable not:\n{data} {type(data)}")


class PreconditionSearchDictError(Exception):
    def __init__(self, search_dict):
        super().__init__(f"\nProvide a dict to perform the search not:\n{search_dict} {type(search_dict)}")


class HighLevelOperatorIteratorError(TypeError):
    def __init__(self):
        super().__init__("The search value for a high level operator must be a container (but not a dict)")
