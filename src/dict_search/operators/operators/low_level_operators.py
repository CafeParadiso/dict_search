import re
from collections.abc import Hashable
from types import FunctionType
from typing import Any


from ... import utils
from .. import exceptions
from ..constants import CONTAINER_TYPE
from ..bases import LowLevelOperator


class Equal(LowLevelOperator):
    name = "eq"

    def implementation(self, val, search_val) -> bool:
        return val == search_val


class NotEqual(LowLevelOperator):
    name = "ne"

    def implementation(self, val, search_val) -> bool:
        return val != search_val


class Greater(LowLevelOperator):
    name = "gt"

    def implementation(self, val, search_val) -> bool:
        return val > search_val


class GreaterEq(LowLevelOperator):
    name = "gte"

    def implementation(self, val, search_val) -> bool:
        return val >= search_val


class LessThen(LowLevelOperator):
    name = "lt"

    def implementation(self, val, search_val) -> bool:
        return val < search_val


class LessThenEq(LowLevelOperator):
    name = "lte"

    def implementation(self, val, search_val) -> bool:
        return val <= search_val


class Is(LowLevelOperator):
    name = "is"

    def implementation(self, val, search_val) -> bool:
        return val is search_val


class In(LowLevelOperator):
    name = "in"

    def implementation(self, val, search_val) -> bool:
        return val in search_val


class NotIn(LowLevelOperator):
    name = "nin"

    def implementation(self, val, search_val) -> bool:
        return val not in search_val


class Contains(LowLevelOperator):
    name = "cont"

    def implementation(self, val, search_val) -> bool:
        return search_val in val


class NotContains(LowLevelOperator):
    name = "ncont"

    def implementation(self, val, search_val) -> bool:
        return search_val not in val


class Regex(LowLevelOperator):
    name = "regex"

    def precondition(self, match_query: Any) -> None:
        if not isinstance(match_query, (re.Pattern, str)):
            raise exceptions.RegexOperatorException(self.name, match_query)

    def implementation(self, val, search_pattern) -> bool:
        if isinstance(search_pattern, re.Pattern):
            return True if search_pattern.search(val) else False
        return True if re.compile(search_pattern).search(val) else False


class Function(LowLevelOperator):
    name = "expr"

    def implementation(self, val, func) -> bool:
        return func(val) if isinstance(func(val), bool) else False


class IsInstance(LowLevelOperator):
    name = "inst"

    def implementation(self, val, search_type) -> bool:
        return isinstance(val, search_type)


class Compare(LowLevelOperator):
    name = "comp"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keys = None
        self.func = None

    def precondition(self, match_query: Any) -> None:
        if not isinstance(match_query, CONTAINER_TYPE) or len(match_query) != 2:
            raise exceptions.CompOperatorTypeError(self.name, CONTAINER_TYPE)
        self.keys, self.func = match_query[0], match_query[1]
        if not (isinstance(self.keys, Hashable) or isinstance(self.keys, list)):
            raise exceptions.CompOperatorFirstArgError(self.name)
        self.keys = self.keys if isinstance(self.keys, list) else [self.keys]
        if not all(isinstance(k, Hashable) for k in self.keys):
            raise exceptions.CompOperatorFirstArgError(self.name)
        if not isinstance(self.func, FunctionType):
            raise exceptions.CompOperatorSecondArgError(self.name)

    def implementation(self, val, search_val, initial_data) -> bool:
        try:
            search_val = utils.get_from_list(initial_data, self.keys)
        except KeyError:
            return False
        result = self.func(val, search_val)
        if not isinstance(result, bool):
            raise exceptions.CompOperatorReturnTypeError(self.name, type(result))
        return result


class GreedySearch(LowLevelOperator):
    name = "greedy"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_depth = 32
        self.candidates = 1
        self.index = 0
        self.iterables = None

    def precondition(self, match_query: Any) -> None:
        if not isinstance(match_query, list) or len(match_query) != 2:
            raise Exception
        keys = match_query[0]
        if not isinstance(keys, (Hashable, list)):
            raise Exception
        if isinstance(keys, list) and not all(isinstance(k, Hashable) for k in keys):
            raise Exception

    def implementation(self, data, keys) -> Any:
        return utils.greedy_search(
            data,
            keys,
            max_depth=self.max_depth,
            candidates=self.candidates,
            index=self.index,
            iterables=self.iterables,
        )
