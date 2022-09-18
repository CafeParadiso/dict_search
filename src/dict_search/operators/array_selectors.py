from .bases import ArraySelector
from .constants import RANGE_PATTERN
from . import exceptions


class Where(ArraySelector):
    name = "where"

    def implementation(self, data, search_value, match_dict):
        return [sub_dict for sub_dict in self.search_instance(data, search_value)], match_dict

    def precondition(self, value):
        if not isinstance(value, self.search_instance.container_type) or len(value) != 2:
            raise exceptions.WhereOperatorError


class Index(ArraySelector):
    name = "index"

    def implementation(self, data, index, match_dict):
        if not isinstance(index, list):
            try:
                return data[index], match_dict
            except IndexError:
                return self.default_return
        values = []
        for i in index:
            try:
                values.append(data[i])
            except IndexError:
                continue
        if not values:
            return self.default_return
        return values, match_dict


class Range(ArraySelector):
    name = "range"

    def implementation(self, data, range_str, match_dict):
        try:
            return eval(f"data[{range_str}]", {"data": data}), match_dict
        except IndexError:
            return self.default_return

    def precondition(self, value):
        super().precondition(value)
        if len(value) != 2:

            raise exceptions.RangeSelectionOperatorError(value)
        range_str = value[0]
        if not isinstance(range_str, str) or not RANGE_PATTERN.match(range_str):
            raise exceptions.RangeSelectionOperatorError(range_str)

    @staticmethod
    def select_precondition(value):
        if not isinstance(value, dict) or len(value) != 1:
            raise exceptions.RangeSelectionOperatorError(value)
