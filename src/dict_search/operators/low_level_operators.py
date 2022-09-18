import re

from .bases import LowLevelOperator
from . import exceptions
from .. import utils


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

    def implementation(self, val, search_pattern) -> bool:
        if isinstance(search_pattern, re.Pattern):
            return True if search_pattern.search(val) else False
        elif isinstance(search_pattern, str):
            return True if re.compile(search_pattern).search(val) else False
        return False


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
