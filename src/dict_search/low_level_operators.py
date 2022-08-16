import abc
import re
from typing import Union
from typing import Type

from . import exceptions
from . import utils


class LowLevelOperator(abc.ABC):
    expected_exc: Union[Exception, tuple] = None
    exc_value: bool = None
    allowed_types: Union[Type, tuple] = None
    ignored_types: Union[Type, tuple] = None

    def __init__(self, search_instance, expected_exc=None, exc_value=None, allowed_types=None, ignored_types=None):
        self.search_instance = search_instance
        self.expected_exc = self.expected_exc or expected_exc
        self.exc_value = self.exc_value or exc_value
        self.allowed_types = self.allowed_types or allowed_types
        self.ignored_types = self.ignored_types or ignored_types
        if self.ignored_types:
            self.implementation = self._ignored_types(self.implementation)
        if self.allowed_types:
            self.implementation = self._allowed_types(self.implementation)

    def _allowed_types(self, func):
        def wrapper(val, arg):
            if not isinstance(val, self.allowed_types):
                return False
            func(val, arg)
        return wrapper

    def _ignored_types(self, func):
        def wrapper(val, arg):
            if isinstance(val, self.ignored_types):
                return False
            func(val, arg)
        return wrapper

    def __call__(self, val, arg) -> bool:
        try:
            return self.implementation(val, arg)
        except Exception as e:
            if self.expected_exc and isinstance(e, self.expected_exc):
                return self.exc_value.get(type(e), False) if isinstance(self.exc_value, dict) else self.exc_value
            raise

    @abc.abstractmethod
    def implementation(self, val, arg) -> bool:
        """Write your operator logic here"""


class Equal(LowLevelOperator):
    def implementation(self, val, search_val) -> bool:
        return val == search_val


class NotEqual(LowLevelOperator):
    def implementation(self, val, search_val) -> bool:
        return val != search_val


class Greater(LowLevelOperator):
    def implementation(self, val, search_val) -> bool:
        return val > search_val


class GreaterEq(LowLevelOperator):
    def implementation(self, val, search_val) -> bool:
        return val >= search_val


class LessThen(LowLevelOperator):
    def implementation(self, val, search_val) -> bool:
        return val < search_val


class LessThenEq(LowLevelOperator):
    def implementation(self, val, search_val) -> bool:
        return val <= search_val


class Is(LowLevelOperator):
    def implementation(self, val, search_val) -> bool:
        return val is search_val


class In(LowLevelOperator):
    def implementation(self, val, search_val) -> bool:
        return val in search_val


class NotIn(LowLevelOperator):
    def implementation(self, val, search_val) -> bool:
        return val not in search_val


class Contains(LowLevelOperator):
    def implementation(self, val, search_val) -> bool:
        return search_val in val


class NotContains(LowLevelOperator):
    def implementation(self, val, search_val) -> bool:
        return search_val not in val


class Regex(LowLevelOperator):
    def implementation(self, val, search_pattern) -> bool:
        if isinstance(search_pattern, re.Pattern):
            return True if search_pattern.search(val) else False
        elif isinstance(search_pattern, str):
            return True if re.compile(search_pattern).search(val) else False
        return False


class Function(LowLevelOperator):
    def implementation(self, val, func) -> bool:
        return func(val) if isinstance(func(val), bool) else False


class IsInstance(LowLevelOperator):
    def implementation(self, val, search_type) -> bool:
        return isinstance(val, search_type)


class Compare(LowLevelOperator):
    def implementation(self, val, search_val) -> bool:
        if not isinstance(search_val, self.search_instance.container_type):
            raise exceptions.HighLevelOperatorIteratorError(self.search_instance.container_type)
        if all(isinstance(x, str) for x in search_val):
            try:
                search_val = utils.get_from_list(self.search_instance._initial_data, search_val)
            except KeyError:
                return False
            else:
                return self.implementation(val, search_val)
        if len(search_val) != 2:
            raise exceptions.CompException
        try:
            comp_val = utils.get_from_list(self.search_instance._initial_data, search_val[0])
        except KeyError:
            return False
        else:
            return search_val[1](val, comp_val)