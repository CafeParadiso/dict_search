import copy
import re

from . import constants
from . import exceptions
from . import utils
from pprint import pprint


class DictSearch:
    def __init__(self, operator_str=None, comparison_exceptions=ValueError):
        self.operator_char = operator_str if isinstance(operator_str, str) else None or "$"

        # matching operators
        self.lop_ne = f"{self.operator_char}ne"
        self.lop_gt = f"{self.operator_char}gt"
        self.lop_gte = f"{self.operator_char}gte"
        self.lop_lt = f"{self.operator_char}lt"
        self.lop_lte = f"{self.operator_char}lte"
        self.lop_is = f"{self.operator_char}is"
        self.lop_in = f"{self.operator_char}in"
        self.lop_nin = f"{self.operator_char}nin"
        self.lop_cont = f"{self.operator_char}cont"
        self.lop_ncont = f"{self.operator_char}ncont"
        self.lop_regex = f"{self.operator_char}regex"
        self.lop_expr = f"{self.operator_char}expr"
        self.lop_inst = f"{self.operator_char}inst"
        self.low_level_operators = [val for key, val in self.__dict__.items() if re.match(r"^lop_.*$", key)]
        self._low_level_comparison_operators = [self.lop_ne, self.lop_gt, self.lop_gte, self.lop_lt, self.lop_lte]

        self.hop_and = f"{self.operator_char}and"
        self.hop_or = f"{self.operator_char}or"
        self.hop_not = f"{self.operator_char}not"
        self.high_level_operators = [val for key, val in self.__dict__.items() if re.match(r"^hop_.*$", key)]

        self.aop_all = f"{self.operator_char}all"
        self.aop_any = f"{self.operator_char}any"
        self.array_operators = [val for key, val in self.__dict__.items() if re.match(r"^aop_.*$", key)]

        self.mop_match = f"{self.operator_char}match"
        self.mop_matchgt = f"{self.operator_char}matchgt"
        self.mop_matchgte = f"{self.operator_char}matchgte"
        self.mop_matchlt = f"{self.operator_char}matchlt"
        self.mop_matchlte = f"{self.operator_char}matchlte"
        self.match_operators = [val for key, val in self.__dict__.items() if re.match(r"^mop_.*$", key)]

        self.as_index = f"{self.operator_char}index"
        self.as_range = f"{self.operator_char}range"
        self.as_where = f"{self.operator_char}where"
        self.array_selectors = [val for key, val in self.__dict__.items() if re.match(r"^as_.*$", key)]
        self._array_selector_map = {
            self.as_index: self._operator_index,
            self.as_range: self._operator_range,
        }

        # select
        self.sel_include = 1
        self.sel_exclude = 0
        self._forbid = None
        self.selection_operators = [self.sel_include, self.sel_exclude]

    def dict_search(self, data, match_dict=None, select_dict=None):
        data = [data] if not utils.iscontainer(data) else data
        if not all(not arg or isinstance(arg, dict) for arg in [match_dict, select_dict]):
            raise exceptions.PreconditionError()
        if match_dict:
            for data_point in data:
                if isinstance(data_point, dict):
                    if all(match for match in self._search(data_point, match_dict)):
                        yield self._select(data_point, select_dict)
        else:
            for data_point in data:
                if isinstance(data_point, dict):
                    yield self._select(data_point, select_dict)

    def _search(self, data, match_dict):
        if isinstance(match_dict, dict) and match_dict:
            for key, value in match_dict.items():
                if key in self.low_level_operators:
                    yield self._low_level_operator(key, data, value)
                elif key in self.high_level_operators:
                    yield self._high_level_operator(key, data, match_dict[key])
                elif key in self.array_operators:
                    yield self._array_operators(key, data, value)
                elif key in self.match_operators:
                    yield self._match_operators(key, data, value)
                elif key in self.array_selectors:
                    yield from self._search(*self._array_selector(key, data, value))
                elif all(isinstance(obj, dict) for obj in [value, data]):
                    yield from self._search(data.get(key), value)
                elif isinstance(data, dict):
                    yield utils.compare(data.get(key), value)
                else:
                    yield False
        else:
            yield utils.compare(data, match_dict)

    def _low_level_operator(self, operator, value, search_value):
        operation_map = {
            self.lop_ne: lambda val, search_val: val != search_val,
            self.lop_gt: lambda val, search_val: val > search_val,
            self.lop_gte: lambda val, search_val: val >= search_val,
            self.lop_lt: lambda val, search_val: val < search_val,
            self.lop_lte: lambda val, search_val: val <= search_val,
            self.lop_is: lambda val, search_val: val is search_val,
            self.lop_in: lambda val, search_val: val in search_val,
            self.lop_nin: lambda val, search_val: val not in search_val,
            self.lop_cont: lambda val, search_val: search_val in val,
            self.lop_ncont: lambda val, search_val: search_val not in val,
            self.lop_regex: lambda val, search_patt: self._operator_regex(val, search_patt),
            self.lop_expr: lambda val, func: func(val) if isinstance(func(val), bool) else False,
            self.lop_inst: lambda val, search_type: isinstance(val, search_type),
        }
        # check if objects have implemented __bool__ in order to compare
        if operator in self._low_level_comparison_operators:
            try:
                bool(value)
            except ValueError:  # TODO expected exceptions
                return False
        try:
            return operation_map[operator](value, search_value)
        except TypeError:
            return False

    @staticmethod
    def _operator_regex(val, search_pattern):
        if isinstance(search_pattern, re.Pattern):
            return True if search_pattern.search(val) else False
        elif isinstance(search_pattern, str):
            return True if re.compile(search_pattern).search(val) else False
        else:
            return False

    def _high_level_operator(self, operator, data, search_container):
        if not utils.iscontainer(search_container):
            raise exceptions.HighLevelOperatorIteratorError
        if utils.isempty(search_container):
            return False
        operator_map = {
            self.hop_and: lambda matches: all(matches),
            self.hop_or: lambda matches: any(matches),
            self.hop_not: lambda matches: not all(matches),
        }
        return operator_map[operator](
            match for search_dict in search_container for match in self._search(data, search_dict)
        )

    def _array_operators(self, operator, data, search_value):
        if not utils.isiter(data) or utils.isempty(data):
            return False
        operator_map = {
            self.aop_all: self._operator_all,
            self.aop_any: self._operator_any,
        }
        return operator_map[operator](data, search_value)

    def _operator_all(self, data, search_value):
        if isinstance(search_value, dict):
            return all(match for d_point in data for match in self._search(d_point, search_value))
        return all(utils.compare(d_point, search_value) for d_point in data)

    def _operator_any(self, data, search_value):
        if isinstance(search_value, dict):
            return any(match for d_point in data for match in self._search(d_point, search_value))
        return any(utils.compare(d_point, search_value) for d_point in data)

    def _match_operators(self, operator, data, search_value):
        try:
            count, search_value = list(search_value.items())[0]
        except (AttributeError, IndexError):
            return False
        try:
            count = int(count)
        except (TypeError, ValueError):
            return False
        operator_map = {
            self.mop_match: [lambda m, c: True if m == c else False, lambda m, c: True if m > c else False, False],
            self.mop_matchgt: [lambda m, c: True if m > c else False, lambda m, c: True if m > c else False, True],
            self.mop_matchgte: [lambda m, c: True if m >= c else False, lambda m, c: True if m >= c else False, True],
            self.mop_matchlt: [lambda m, c: True if m < c else False, lambda m, c: True if m >= c else False, False],
            self.mop_matchlte: [lambda m, c: True if m <= c else False, lambda m, c: True if m > c else False, False],
        }
        default_args = operator_map[operator][0], count, operator_map[operator][1], operator_map[operator][2]

        if utils.iscontainer(search_value):  # match is being used as high level operator
            return utils.shortcircuit_counter(
                iter(match for search_dict in search_value for match in self._search(data, search_dict)), *default_args
            )
        elif isinstance(search_value, dict):  # match is being used as array operator
            return utils.shortcircuit_counter(
                iter(all([m for m in self._search(data_point, search_value)]) for data_point in data), *default_args
            )
        return utils.shortcircuit_counter(  # match is being used as array operator to compare each value
            iter(utils.compare(d_point, search_value) for d_point in data), *default_args
        )

    def _array_selector(self, operator_type, data, search_value):
        if operator_type == self.as_where:
            return self._operator_where(data, search_value)
        try:
            operator, search_value = list(search_value.items())[0]
        except AttributeError:
            raise exceptions.ArraySelectorFormatException(operator_type)
        try:
            return self._array_selector_map[operator_type](data, operator), search_value
        except (TypeError, IndexError):
            return [], {}

    def _operator_where(self, data, search_value):
        if not utils.iscontainer(search_value) or len(search_value) != 2:
            raise exceptions.WhereOperatorError
        array_match_dict, match_dict = search_value
        return [sub_dict for sub_dict in self.dict_search(data, array_match_dict)], match_dict

    @staticmethod
    def _operator_index(data, index):
        return data[int(index)]

    @staticmethod
    def _operator_range(data, range_str):
        if not utils.israngestr(range_str):
            return
        return eval(f"data[{range_str}]", {"data": data})

    def _select(self, data, selection_dict):
        selected_dict = {}
        self._apply_selection(data, selection_dict, selected_dict)
        return selected_dict or data

    def _apply_selection(self, data, selection_dict, selected_dict, prev_keys=None, original_data=None):
        prev_keys = prev_keys if prev_keys else []
        original_data = copy.deepcopy(data) if not original_data else original_data
        if isinstance(selection_dict, dict) and data:
            for key, val in selection_dict.items():
                if key in self.array_selectors:
                    self._from_array_selector(key, data, val, selected_dict, prev_keys, original_data)
                elif val in self.selection_operators:
                    prev_keys.append(key)
                    self._build_selected_dict(key, val, data, selected_dict, prev_keys, original_data)
                    prev_keys.pop(-1)
                else:
                    prev_keys.append(key)
                    self._apply_selection(data.get(key), val, selected_dict, prev_keys, original_data)
                    prev_keys.pop(-1)

    def _from_array_selector(self, operator_type, data, search_value, selected_dict, prev_keys, original_data):
        if utils.isempty(data):
            return
        try:
            operator, search_value = list(search_value.items())[0]
        except AttributeError:
            raise exceptions.ArraySelectorFormatException(operator_type)
        operator_map = {
            self.as_index: self._operator_index_select,
            self.as_range: self._operator_range_select,
            self.as_where: self._operator_where_select,
        }
        if search_value in self.selection_operators:
            try:
                value = operator_map[operator_type](data, operator, search_value)
                if value:
                    utils.set_from_list(selected_dict, prev_keys, value)
            except (TypeError, IndexError):
                return
        else:
            try:
                values = self._array_selector_map[operator_type](data, operator)
            except (TypeError, IndexError):
                return
            values = [values] if not utils.iscontainer(values) else values
            selected_values = []
            for val in values:
                selected_val = {}
                self._apply_selection(val, search_value, selected_val)
                selected_values.append(selected_val)
            utils.set_from_list(selected_dict, prev_keys, selected_values)

    def _operator_index_select(self, data, index, select_op):
        if select_op == self.sel_include:
            return copy.deepcopy(data)[int(index)]
        elif select_op == self.sel_exclude:
            data_copy = copy.deepcopy(data)
            data_copy.pop(int(index))
            return data_copy

    def _operator_range_select(self, data, range_str, select_op):
        if select_op == self.sel_include:
            return self._operator_range(data, range_str)
        elif select_op == self.sel_exclude:
            if not utils.israngestr(range_str):
                return
            data_copy = copy.deepcopy(data)
            exec(f"del data[{range_str}]", {"data": data_copy})
            return data_copy

    def _operator_where_select(self):
        pass

    def _build_selected_dict(self, key, operator, data, selected_dict, prev_keys, original_data):
        if operator == self._forbid:
            return
        if operator == self.sel_include:
            self._forbid = self.sel_exclude
            self._include(key, data, selected_dict, prev_keys)
        else:
            self._forbid = self.sel_include
            self._exclude(original_data, selected_dict, prev_keys)

    @staticmethod
    def _include(key, data, selected_dict, prev_keys):
        value = copy.deepcopy(data).pop(key, None)
        if value:
            utils.set_from_list(selected_dict, prev_keys, value)

    @staticmethod
    def _exclude(original_data, selected_dict, prev_keys):
        if not selected_dict:
            selected_dict.update(copy.deepcopy(original_data))
        utils.pop_from_list(selected_dict, prev_keys)
