class OperatorCharError(TypeError):
    def __init__(self, operator_str):
        super().__init__(f"Operator chars must be 'str' not:\n{operator_str}|{type(operator_str)}")


class PreconditionDataError(Exception):
    def __init__(self, data):
        super().__init__(f"\nData must be an iterable not:\n{data} {type(data)}")


class PreconditionSearchDictError(Exception):
    def __init__(self, search_dict):
        super().__init__(f"\nProvide a dict to perform the search not:\n{search_dict} {type(search_dict)}")


class HighLevelOperatorIteratorError(TypeError):
    def __init__(self):
        super().__init__("High level operators should be a list, tuple, set or generator")
