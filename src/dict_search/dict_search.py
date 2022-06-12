from collections import abc
import re

from . import exceptions
from . import utils
from pprint import pprint


class DictSearch:
    def __init__(self, operator_str=None, eval_exc=None, exc_truth_value=False, consumable_iterator=None):
        self.operator_char = operator_str if isinstance(operator_str, str) else "$"
        self._eval_exc = eval_exc
        self._exc_truth_value = exc_truth_value
        self._consumable_iterator = consumable_iterator

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
        data = [data] if isinstance(data, dict) or not utils.isiter(data) else data
        if not all(not arg or isinstance(arg, dict) for arg in [match_dict, select_dict]):
            raise exceptions.PreconditionError()
        for data_point in data:
            if not isinstance(data_point, dict):
                continue
            if all(match for match in self._search(data_point, match_dict)) if match_dict else True:
                yield self._select(data_point, select_dict) if select_dict else data_point

    def _search(self, data, match_dict):
        if isinstance(match_dict, dict) and match_dict:
            for key, value in match_dict.items():
                if key in self.low_level_operators:
                    yield self._low_level_operator(key, data, value)
                elif key in self.high_level_operators:
                    yield self._high_level_operator(key, data, value)
                elif key in self.array_operators:
                    yield self._array_operators(key, data, value)
                elif key in self.match_operators:
                    yield self._match_operators(key, data, value)
                elif key in self.array_selectors:
                    yield from self._search(*self._array_selector(key, data, value))
                elif all(isinstance(obj, dict) for obj in [value, data]):
                    yield from self._search(self._assign_consumed_iterator(data, key, value, data.get(key)), value)
                elif isinstance(data, dict):
                    yield self._compare(data.get(key), value)
                else:
                    yield False
        else:
            yield self._compare(data, match_dict)

    def _assign_consumed_iterator(self, data, key, value, nested_data):
        """Assign to original data the consumed generator to avoid bugs while performing matching and after return it

        It will be applied if the next search operator(arg value) is:
        -array operator, array selector or match operator being used as array operator
        This behaviour can be avoided by specfiying an iterator type through the exhaustible_iterator parameter
        """
        if (
            not isinstance(nested_data, self._consumable_iterator) and isinstance(nested_data, abc.Iterator)
            if self._consumable_iterator
            else isinstance(nested_data, abc.Iterator)
            and isinstance(value, dict)
            and value
            and (
                list(value.keys())[0] in self.array_operators + self.array_selectors
                or (list(value.keys())[0] in self.match_operators and not utils.isoperator(list(value.values())[0]))
            )
        ):
            nested_data = list(nested_data)
            data[key] = nested_data
        return nested_data

    def _compare(self, data, comparison):
        try:
            if data == comparison:
                return True
            return False
        except self._eval_exc or Exception:
            if self._eval_exc:
                return self._exc_truth_value
            raise

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
        # prematurely check if __bool__ is implemented in order to avoid unexpected errors on all() in dict_search()
        if operator in self._low_level_comparison_operators:
            try:
                bool(value)
            except self._eval_exc or Exception:
                if not self._eval_exc:
                    raise
                return self._exc_truth_value
        try:
            return operation_map[operator](value, search_value)
        except self._eval_exc or TypeError:
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
        if not utils.isoperator(search_container):
            raise exceptions.HighLevelOperatorIteratorError
        if not search_container:
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
        if not utils.isiter(data):
            return False
        operator_map = {
            self.aop_all: self._operator_all,
            self.aop_any: self._operator_any,
        }
        return operator_map[operator](data, search_value)

    def _operator_all(self, data, search_value):
        if isinstance(search_value, dict):
            values = [match for d_point in data for match in self._search(d_point, search_value)]
        else:
            values = [self._compare(d_point, search_value) for d_point in data]
        return False if not values else all(values)

    def _operator_any(self, data, search_value):
        if isinstance(search_value, dict):
            return any(match for d_point in data for match in self._search(d_point, search_value))
        return any(self._compare(d_point, search_value) for d_point in data)

    def _match_operators(self, operator, data, search_value):
        try:
            count, search_value = list(search_value.items())[0]
            assert isinstance(count, int)
        except (AttributeError, IndexError, AssertionError):
            raise exceptions.MatchOperatorError(search_value)
        operator_map = {
            self.mop_match: [lambda m, c: True if m == c else False, lambda m, c: True if m > c else False, False],
            self.mop_matchgt: [lambda m, c: True if m > c else False, lambda m, c: True if m > c else False, True],
            self.mop_matchgte: [lambda m, c: True if m >= c else False, lambda m, c: True if m >= c else False, True],
            self.mop_matchlt: [lambda m, c: True if m < c else False, lambda m, c: True if m >= c else False, False],
            self.mop_matchlte: [lambda m, c: True if m <= c else False, lambda m, c: True if m > c else False, False],
        }
        default_args = operator_map[operator][0], count, operator_map[operator][1], operator_map[operator][2]

        if utils.isoperator(search_value):  # match is being used as high level operator
            return utils.shortcircuit_counter(
                iter(match for search_dict in search_value for match in self._search(data, search_dict)), *default_args
            )
        elif isinstance(search_value, dict):  # match is being used as array operator
            return utils.shortcircuit_counter(
                iter(all([m for m in self._search(data_point, search_value)]) for data_point in data), *default_args
            )
        return utils.shortcircuit_counter(  # match is being used as array op. to compare each value in the iterable
            iter(self._compare(d_point, search_value) for d_point in data), *default_args
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
        if not utils.isoperator(search_value) or len(search_value) != 2:
            raise exceptions.WhereOperatorError
        array_match_dict, match_dict = search_value
        return [sub_dict for sub_dict in self.dict_search(data, array_match_dict)], match_dict

    @staticmethod
    def _operator_index(data, index):
        return data[int(index)]

    @staticmethod
    def _operator_range(data, range_str):
        if not isinstance(range_str, str) or not utils.israngestr(range_str):
            return
        return eval(f"data[{range_str}]", {"data": data})

    def _select(self, data, selection_dict):
        selected_dict = {}
        self._apply_selection(data, selection_dict, selected_dict)
        return selected_dict

    def _apply_selection(self, data, selection_dict, selected_dict, prev_keys=None, original_data=None):
        prev_keys = prev_keys if prev_keys else []
        original_data = data if not original_data else original_data
        if isinstance(selection_dict, dict) and data:
            for key, val in selection_dict.items():
                if key == self.as_where:
                    self._operator_sel_where(data, val, selected_dict, prev_keys, original_data)
                elif key in [self.as_index, self.as_range]:
                    self._from_array_selector(key, data, val, selected_dict, prev_keys, original_data)
                elif isinstance(data, dict) and key not in data.keys():
                    continue
                elif val in self.selection_operators and isinstance(data, dict):
                    prev_keys.append(key)
                    self._build_selected_dict(key, val, data, selected_dict, prev_keys, original_data)
                    prev_keys.pop(-1)
                elif utils.isiter(data) and not isinstance(data, (str, bytes, bytearray, abc.Mapping)):
                    # iterate over data and apply selection over each data_point
                    self._apply_to_container(data, selection_dict, selected_dict, prev_keys, original_data)
                else:
                    prev_keys.append(key)
                    self._apply_selection(
                        self._assign_consumed_iterator(data, key, val, data.get(key)),
                        val,
                        selected_dict,
                        prev_keys,
                        original_data,
                    )
                    prev_keys.pop(-1)

    def _apply_to_container(self, data, selection_dict, selected_dict, prev_keys, original_data):
        values = []
        for data_point in data:
            sel_dict = {}
            self._apply_selection(data_point, selection_dict, sel_dict)
            if sel_dict:
                values.append(sel_dict)
        if self._forbid != self.sel_exclude and not selected_dict:
            selected_dict.update(original_data)
        if values:
            utils.set_from_list(selected_dict, prev_keys, values)

    def _operator_sel_where(self, data, search_value, selected_dict, prev_keys, original_data):
        if not utils.isoperator(search_value) or len(search_value) != 2:
            raise exceptions.WhereOperatorError
        match_dict, operator = search_value
        if isinstance(operator, dict):
            self._apply_to_container(
                self.dict_search(data, match_dict), operator, selected_dict, prev_keys, original_data
            )
        else:
            values = []
            for data_point in data:
                if operator == self.sel_include:
                    if all(match for match in self._search(data_point, match_dict)):
                        values.append(data_point)
                elif operator == self.sel_exclude:
                    if not selected_dict:
                        selected_dict.update(original_data)
                    if not all(match for match in self._search(data_point, match_dict)):
                        values.append(data_point)
            if values:
                utils.set_from_list(selected_dict, prev_keys, values)

    def _from_array_selector(self, operator_type, data, search_value, selected_dict, prev_keys, original_data):
        try:
            operator, search_value = list(search_value.items())[0]
        except AttributeError:
            raise exceptions.ArraySelectorFormatException(operator_type)
        operator_map = {
            self.as_index: self._operator_sel_index,
            self.as_range: self._operator_sel_range,
        }
        if search_value in self.selection_operators:
            try:
                utils.set_from_list(selected_dict, prev_keys, operator_map[operator_type](data, operator, search_value))
            except (TypeError, IndexError):
                return
            return
        try:
            values = self._array_selector_map[operator_type](data, operator)
        except (TypeError, IndexError):
            return
        utils.set_from_list(original_data, prev_keys, values)
        self._apply_selection(values, search_value, selected_dict, prev_keys, original_data)

    def _operator_sel_index(self, data, index, select_op):
        if select_op == self.sel_include:
            return data[int(index)]
        elif select_op == self.sel_exclude:
            data.pop(int(index))
            return data

    def _operator_sel_range(self, data, range_str, select_op):
        if select_op == self.sel_include:
            return self._operator_range(data, range_str)
        elif select_op == self.sel_exclude:
            if not isinstance(range_str, str) or not utils.israngestr(range_str):
                return
            exec(f"del data[{range_str}]", {"data": data})
            return data

    def _build_selected_dict(self, key, operator, data, selected_dict, prev_keys, original_data):
        if operator == self._forbid:
            return
        if operator == self.sel_include:
            self._forbid = self.sel_exclude
            utils.set_from_list(selected_dict, prev_keys, data.pop(key, None))
        elif operator == self.sel_exclude:
            self._forbid = self.sel_include
            if not selected_dict:
                selected_dict.update(original_data)
            utils.pop_from_list(selected_dict, prev_keys)
