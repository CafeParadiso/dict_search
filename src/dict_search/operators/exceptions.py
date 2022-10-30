from re import Pattern

from . import constants


class OperatorImplementationAttrTypeError(TypeError):
    def __init__(self, cls, attr):
        super().__init__(
            f"\n\nImplement '{attr}' as a class variable not as {type(getattr(cls, attr))}, e.g:\n"
            f"class {cls.__name__}(Operator):\n    {attr} = ..."
        )


class OperatorImplementationOverrideError(TypeError):
    def __init__(self, attr):
        super().__init__(f"\n\n You cannot override the attribute '{attr}'")


class OperatorImplementationNameError(TypeError):
    def __init__(self, cls, attr):
        super().__init__(
            f"\n\nClass attribute '{attr}' should be {str}, e.g:\n"
            f"class {cls.__name__}(Operator):\n    {attr} = '{cls.__name__.lower()}'"
        )


class OperatorExpectedExcArgError(TypeError):
    def __init__(self, prop, attr_type):
        super().__init__(
            f"Values for {prop} should be any of these types:\n"
            f"-Exception\n"
            f"-(..., Exception)\n"
            f"-{{Exception: {attr_type}}}\n"
        )


class OperatoTypeCheckerError(TypeError):
    def __init__(self, func_name):
        super().__init__(f"'{func_name}' should be type or tuple[..., type]")


class OperatorDefaultReturnError(TypeError):
    def __init__(self, prop, attr_name, attr):
        super().__init__(f"Provide a value for {prop} " f"of the same type as {attr_name} :\n" f"{type(attr)}")


class SliceSelectionOperatorError(SyntaxError):
    def __init__(self, operator):
        super().__init__(
            f"Use a slicing string matching any pattern in {constants.SLICING_PATTERN} not:\n '{operator}'"
        )


class WhereOperatorError(SyntaxError):
    def __init__(self):
        super().__init__(
            "The search value for 'where' must be a list of two elements: [{array_match_condition}, {match_dict}]"
        )


class HighLevelOperatorIteratorError(SyntaxError):
    def __init__(self, container_type, match_query):
        super().__init__(f"The search value for a high level operator must be a non empty {container_type}\n.")


class MatchOperatorError(SyntaxError):
    def __init__(self, op_name):
        super().__init__(
            f"Any match operator must be a dict like {{'{op_name}': count(int): search_val}}"
        )


class MatchOperatorCountMismatch(SyntaxError):
    def __init__(self, thresh, search_operator):
        super().__init__(
            f"The threshold value for a match operator should be less or equal then the number of queries"
            f"thresh: {thresh} > nº of search operators: {len(search_operator)}"
        )


class ArraySelectorFormatException(SyntaxError):
    def __init__(self, operator):
        super().__init__(f"Use a list as '{operator}' operator:\n[':2', {{'k': 'v'}}]")


class WhereIteratorException(TypeError):
    def __init__(self, operator, data):
        super().__init__(
            f"\nBy default '{operator}' does not support Iterators, '{type(data)}' was found.\n"
            f"Set a type for the attribute 'consumable_iterators' to consume the iterator and apply the operator, ie:\n"
            f"DictSearch(consumable_iterators=Iterator)"
            f"\nOr set an expected exception for the operator to avoid iterator consumption and the exception:\n"
            f"DictSearch(ops_config={{'expected_exc': '{self.__class__.__name__}'}})"
        )


class CompOperatorTypeError(TypeError):
    def __init__(self, op_name, expected_type):
        super().__init__(f"Operator '{op_name}' should be of type '{expected_type}' and length 2")


class CompOperatorFirstArgError(ValueError):
    def __init__(self, op_name):
        super().__init__(
            f"\n\nThe first value for '{op_name}' should be a single object or list of objects\n"
            "that can be used as dict keys:\n"
            "'a', 1, ['b', 'c'], ...\n\n"
            "data = {'a': 1, 'b': {'c': 2}}\n"
            "query = {'a': {'$comp': [['b', 'c'], lambda x, y: x == y]}}\n"
        )


class CompOperatorSecondArgError(ValueError):
    def __init__(self, op_name):
        super().__init__(
            f"\n\nThe second value for '{op_name}' should be a function with two arguments that returns type 'bool'\n\n"
            "data = {'a': 1, 'b': {'c': 2}}\n"
            "query = {'a': {'$comp': [['b', 'c'], lambda x, y: x == y]}}\n\n"
            "'x' corresponds to the value of 'a' (1) and 'y' to the nested value ['b', 'c'] (2)"
        )


class CompOperatorReturnTypeError(ValueError):
    def __init__(self, op_name, return_obj_type):
        super().__init__(
            f"\n\nThe function provided for '{op_name}' should return an object of type {bool}\n"
            f"Instead it returned {return_obj_type}"
        )


class RegexOperatorException(SyntaxError):
    def __init__(self, op_name, query):
        super().__init__(
            f"The value for '{op_name}' must be of type 'str' or '{Pattern.__name__}' not: '{type(query)}'"
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
