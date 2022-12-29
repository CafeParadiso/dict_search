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

    def __init__(self, search_val, **kwargs):
        super().__init__(**kwargs)
        self.comp = search_val

    def implementation(self, data) -> bool:
        return self.comp == data


class NotEqual(LowLevelOperator):
    name = "ne"

    def __init__(self, search_val, **kwargs):
        super().__init__(**kwargs)
        self.comp = search_val

    def implementation(self, data) -> bool:
        return self.comp != data


class Greater(LowLevelOperator):
    name = "gt"

    def __init__(self, search_val, **kwargs):
        super().__init__(**kwargs)
        self.comp = search_val

    def implementation(self, data) -> bool:
        return data > self.comp


class GreaterEq(LowLevelOperator):
    name = "gte"

    def __init__(self, search_val, **kwargs):
        super().__init__(**kwargs)
        self.comp = search_val

    def implementation(self, data) -> bool:
        return data >= self.comp


class LessThen(LowLevelOperator):
    name = "lt"

    def __init__(self, search_val, **kwargs):
        super().__init__(**kwargs)
        self.comp = search_val

    def implementation(self, data) -> bool:
        return data < self.comp


class LessThenEq(LowLevelOperator):
    name = "lte"

    def __init__(self, search_val, **kwargs):
        super().__init__(**kwargs)
        self.comp = search_val

    def implementation(self, data) -> bool:
        return data <= self.comp


class Is(LowLevelOperator):
    name = "is"

    def __init__(self, search_val, **kwargs):
        super().__init__(**kwargs)
        self.comp = search_val

    def implementation(self, data) -> bool:
        return data is self.comp


class In(LowLevelOperator):
    name = "in"

    def __init__(self, search_val, **kwargs):
        super().__init__(**kwargs)
        self.comp = search_val

    def implementation(self, data) -> bool:
        return data in self.comp


class NotIn(LowLevelOperator):
    name = "nin"

    def __init__(self, search_val, **kwargs):
        super().__init__(**kwargs)
        self.comp = search_val

    def implementation(self, data) -> bool:
        return data not in self.comp


class Contains(LowLevelOperator):
    name = "cont"

    def __init__(self, search_val, **kwargs):
        super().__init__(**kwargs)
        self.comp = search_val

    def implementation(self, data) -> bool:
        return self.comp in data


class NotContains(LowLevelOperator):
    name = "ncont"

    def __init__(self, search_val, **kwargs):
        super().__init__(**kwargs)
        self.comp = search_val

    def implementation(self, data) -> bool:
        return self.comp not in data


class Regex(LowLevelOperator):
    name = "regex"

    def __init__(self, pattern, **kwargs):
        super().__init__(**kwargs)
        if isinstance(pattern, str):
            self.pattern = re.compile(pattern)
        elif isinstance(pattern, re.Pattern):
            self.pattern = pattern
        else:
            raise exceptions.RegexOperatorException(self.name, pattern)

    def precondition(self, match_query: Any) -> None:
        if not isinstance(match_query, (re.Pattern, str)):
            raise exceptions.RegexOperatorException(self.name, match_query)

    def implementation(self, data) -> bool:
        return True if self.pattern.search(data) else False


class Function(LowLevelOperator):
    name = "func"

    def __init__(self, function, **kwargs):
        super().__init__(**kwargs)
        self.function = function

    def implementation(self, data) -> bool:
        value = self.function(data)
        return value if isinstance(value, bool) else False


class IsInstance(LowLevelOperator):
    name = "inst"

    def __init__(self, data_type, **kwargs):
        super().__init__(**kwargs)
        self.data_type = data_type

    def implementation(self, data) -> bool:
        return isinstance(data, self.data_type)


class Compare(LowLevelOperator):
    name = "comp"

    def __init__(self, keys, func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not (
            isinstance(keys, Hashable) or (isinstance(keys, list) and all(map(lambda x: isinstance(x, Hashable), keys)))
        ):
            raise exceptions.CompOperatorFirstArgError(self.name)
        self.keys = keys if isinstance(keys, list) else [keys]
        if not isinstance(func, FunctionType):
            raise exceptions.CompOperatorSecondArgError(self.name)
        self.func = func

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

    def implementation(self, val, initial_data) -> bool:
        try:
            search_val = utils.get_from_list(initial_data, self.keys)
        except KeyError:
            return False
        result = self.func(val, search_val)
        if not isinstance(result, bool):
            raise exceptions.CompOperatorReturnTypeError(self.name, type(result))
        return result


class Find(LowLevelOperator):
    name = "find"

    def __init__(self, keys, *args, max_depth: int = 32, candidates: int = 1, index: int = 1, iterables=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.keys = keys
        self.max_depth = max_depth
        self.candidates = candidates
        self.index = index
        self.iterables = iterables

    def precondition(self, match_query: Any) -> None:
        if not isinstance(match_query, list) or len(match_query) != 2:
            raise Exception
        keys = match_query[0]
        if not isinstance(keys, (Hashable, list)):
            raise Exception
        if isinstance(keys, list) and not all(isinstance(k, Hashable) for k in keys):
            raise Exception

    def implementation(self, data) -> Any:
        return utils.find_value(
            data,
            self.keys,
            max_depth=self.max_depth,
            candidates=self.candidates,
            index=self.index,
            iterables=self.iterables,
        )
