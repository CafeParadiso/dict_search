from collections import abc
from copy import copy
import re

from . import exceptions
from . import utils
from pprint import pprint


def _copy_data(func):
    def wrapper(*args, **kwargs):
        try:
            data = kwargs["data"][:]
        except TypeError:
            return
        kwargs["data"] = data
        func(*args, **kwargs)
    return wrapper


class DictSearch:
    def __init__(
        self,
        operator_str=None,
        eval_exc=None,
        exc_truth_value=False,
        consumable_iterators=None,
        coerce_list=False,
    ):
        self.operator_char = operator_str if isinstance(operator_str, str) else "$"
        self._eval_exc = eval_exc
        self._exc_truth_value = exc_truth_value
        self._consumable_iterators = consumable_iterators
        if consumable_iterators:
            self._consumable_iterators = (
                consumable_iterators if isinstance(consumable_iterators, list) else [consumable_iterators]
            )
        self._coerce_list = coerce_list

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
        self.lop_comp = f"{self.operator_char}comp"
        self._initial_data = {}
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

        # select
        self.sel_include = 1
        self.sel_exclude = 0
        self._used = None
        self.selection_operators = [self.sel_include, self.sel_exclude]
        self.sel_array = f"{self.operator_char}array"

    def dict_search(self, data, match_dict=None, select_dict=None):
        data = [data] if isinstance(data, dict) or not utils.isiter(data) else data
        if not all(not arg or isinstance(arg, dict) for arg in [match_dict, select_dict]):
            raise exceptions.PreconditionError()
        for data_point in data:
            if not isinstance(data_point, dict) or not data_point:
                continue
            self._initial_data.clear()
            if all(match for match in self._match(data_point, match_dict)) if match_dict else True:
                self._initial_data.clear()
                if select_dict:
                    selected_dict = self._select(data_point, select_dict)
                    if not selected_dict:
                        continue
                    yield selected_dict
                else:
                    yield data_point

    def _match(self, data, match_dict):
        self._initial_data = self._initial_data if self._initial_data else data.copy()
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
                    yield from self._match(*self._array_selector(key, data, value))
                elif all(isinstance(obj, dict) for obj in [value, data]):
                    yield from self._match(self._assign_consumed_iterator(data, key, value), value)
                elif isinstance(data, dict):
                    yield self._compare(data.get(key), value)
                else:
                    yield False
        else:
            yield self._compare(data, match_dict)

    def _assign_consumed_iterator(self, data, key, value, operator_check=True):
        """Assign to original data the consumed generator to avoid bugs while performing matching and after return it

        It will be applied if the next search operator(arg value) is:
        -array operator, array selector or match operator being used as array operator
        This behaviour can be avoided by specfiying an iterator type through the exhaustible_iterator parameter
        """
        try:
            nested_data = data.get(key)
        except AttributeError:
            return
        if (
            not isinstance(nested_data, *self._consumable_iterators) and isinstance(nested_data, abc.Iterator)
            if self._consumable_iterators
            else isinstance(nested_data, abc.Iterator)
            and isinstance(value, dict)
            and value
            and (
                list(value.keys())[0] in self.array_operators + self.array_selectors
                or (list(value.keys())[0] in self.match_operators and not self._iscontainer(list(value.values())[0]))
                if operator_check
                else True
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

    @staticmethod
    def _iscontainer(obj):
        if isinstance(obj, list):
            return True
        return False

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
            self.lop_comp: lambda val, search_val: self._operator_comp(val, search_val),
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

    def _operator_comp(self, val, search_val):
        if not self._iscontainer(search_val):
            raise exceptions.HighLevelOperatorIteratorError
        if all(isinstance(x, str) for x in search_val):
            try:
                search_val = utils.get_from_list(self._initial_data, search_val)
            except KeyError:
                return False
            else:
                return self._compare(val, search_val)
        if len(search_val) != 2:
            raise exceptions.CompException
        try:
            comp_val = utils.get_from_list(self._initial_data, search_val[0])
        except KeyError:
            return False
        else:
            return search_val[1](val, comp_val)

    def _high_level_operator(self, operator, data, search_container):
        if not self._iscontainer(search_container):
            raise exceptions.HighLevelOperatorIteratorError
        if not search_container:
            return False
        operator_map = {
            self.hop_and: lambda matches: all(matches),
            self.hop_or: lambda matches: any(matches),
            self.hop_not: lambda matches: not all(matches),
        }
        return operator_map[operator](
            match for search_dict in search_container for match in self._match(data, search_dict)
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
            values = [match for d_point in data for match in self._match(d_point, search_value)]
        else:
            values = [self._compare(d_point, search_value) for d_point in data]
        return False if not values else all(values)

    def _operator_any(self, data, search_value):
        if isinstance(search_value, dict):
            return any(match for d_point in data for match in self._match(d_point, search_value))
        return any(self._compare(d_point, search_value) for d_point in data)

    def _match_operators(self, operator, data, search_value):
        try:
            tresh, search_value = list(search_value.items())[0]
            assert isinstance(tresh, int)
        except (AttributeError, IndexError, AssertionError):
            raise exceptions.MatchOperatorError(search_value)
        operator_map = {
            self.mop_match: [lambda m, c: True if m == c else False, lambda m, c: True if m > c else False, False],
            self.mop_matchgt: [lambda m, c: True if m > c else False, lambda m, c: True if m > c else False, True],
            self.mop_matchgte: [lambda m, c: True if m >= c else False, lambda m, c: True if m >= c else False, True],
            self.mop_matchlt: [lambda m, c: True if m < c else False, lambda m, c: True if m >= c else False, False],
            self.mop_matchlte: [lambda m, c: True if m <= c else False, lambda m, c: True if m > c else False, False],
        }
        default_args = operator_map[operator][0], tresh, operator_map[operator][1], operator_map[operator][2]

        if self._iscontainer(search_value):  # match is being used as high level operator
            return utils.shortcircuit_counter(
                iter(match for search_dict in search_value for match in self._match(data, search_dict)), *default_args
            )
        elif isinstance(search_value, dict):  # match is being used as array operator
            return utils.shortcircuit_counter(
                iter(all([m for m in self._match(data_point, search_value)]) for data_point in data), *default_args
            )
        return utils.shortcircuit_counter(  # match is being used as array op. to compare each value in the iterable
            iter(self._compare(d_point, search_value) for d_point in data), *default_args
        )

    def _array_selector(self, operator_type, data, search_value):
        if operator_type == self.as_where:
            return self._operator_where(data, search_value)
        elif operator_type == self.as_index and isinstance(search_value, list) and len(search_value) == 2:
            operator, search_value = search_value[0], search_value[1]
        elif isinstance(search_value, dict) and len(search_value):
            operator, search_value = list(search_value.items())[0]
        else:
            raise exceptions.ArraySelectorFormatException(operator_type)
        try:
            return {self.as_index: self._operator_index, self.as_range: self._operator_range}[operator_type](
                data, operator
            ), search_value
        except (TypeError, IndexError, KeyError):
            return [], {}

    def _operator_where(self, data, search_value):
        if not self._iscontainer(search_value) or len(search_value) != 2:
            raise exceptions.WhereOperatorError
        array_match_dict, match_dict = search_value
        return [sub_dict for sub_dict in self.dict_search(data, array_match_dict)], match_dict

    @staticmethod
    def _operator_index(data, index):
        if not isinstance(index, list):
            return data[index]
        values = []
        for i in index:
            values.append(data[i])
        return values

    @staticmethod
    def _operator_range(data, range_str):
        if not isinstance(range_str, str) or not utils.israngestr(range_str):
            raise exceptions.RangeSelectionOperatorError(range_str)
        return eval(f"data[{range_str}]", {"data": data})

    def _select(self, data, selection_dict):
        selected_dict = {}
        self._apply_selection(data, selection_dict, selected_dict)
        return selected_dict

    def _apply_selection(self, data, selection_dict, selected_dict, prev_keys=None, original_data=None):
        prev_keys = prev_keys if prev_keys else []
        original_data = original_data if original_data else data.copy()
        if isinstance(selection_dict, dict) and data:
            for key, val in selection_dict.items():
                if key == self.as_where and prev_keys:
                    self._operator_sel_where(data, val, selected_dict, prev_keys, original_data)
                elif key == self.as_index and prev_keys:
                    self._operator_sel_index(data, val, selected_dict, prev_keys, original_data)
                elif key == self.as_range and prev_keys:
                    self._operator_sel_range(data, val, selected_dict, prev_keys, original_data)
                elif isinstance(data, dict) and key not in data.keys():
                    continue
                elif val in self.selection_operators and isinstance(data, dict):
                    prev_keys.append(key)
                    self._build_dict(val, data.get(key), selected_dict, prev_keys, original_data)
                    prev_keys.pop(-1)
                elif key == self.sel_array and utils.isiter(data):
                    self._apply_to_container(data, selection_dict, selected_dict, prev_keys, original_data)
                else:
                    prev_keys.append(key)
                    self._apply_selection(
                        self._assign_consumed_iterator(data, key, val, operator_check=False),
                        val,
                        selected_dict,
                        prev_keys,
                        original_data,
                    )
                    prev_keys.pop(-1)

    def _select_iter(self, data, selection_dict):
        values = []
        for d_point in data:
            if not isinstance(d_point, dict):
                continue
            sel_dict = self._select(d_point, selection_dict)
            if sel_dict:
                values.append(sel_dict)
        return values

    def _apply_to_container(self, data, selection_dict, selected_dict, prev_keys, original_data):
        values = self._select_iter(data, selection_dict)
        if not values:
            return
        excl = lambda: self._exclude(selected_dict, prev_keys, original_data, values)
        self._build_dict(self._used, values, selected_dict, prev_keys, original_data, excl_func=excl)

    def _operator_sel_where(self, data, search_value, selected_dict, prev_keys, original_data):
        if not isinstance(search_value, list) or len(search_value) != 2:
            raise exceptions.WhereOperatorError
        match_dict, operator = search_value
        if isinstance(operator, dict):
            self._apply_to_container(
                self.dict_search(data, match_dict), operator, selected_dict, prev_keys, original_data
            )
        else:
            incl = lambda: self.where_incl(match_dict, selected_dict, data, prev_keys)
            excl = lambda: self.where_excl(match_dict, selected_dict, data, prev_keys, original_data)
            self._build_dict(operator, [], selected_dict, prev_keys, original_data, incl_func=incl, excl_func=excl)

    def where_incl(self, match_dict, selected_dict, data, prev_keys):
        values = [d_point for d_point in data if all(self._match(d_point, match_dict))]
        utils.set_from_list(selected_dict, prev_keys, values) if values else None

    def where_excl(self, match_dict, selected_dict, data, prev_keys, original_data):
        values = [d_point for d_point in data if not all(self._match(d_point, match_dict))]
        if values == data:
            return
        if values:
            self._exclude(selected_dict, prev_keys, original_data, values)

    def _operator_sel_index(self, data, select_op, selected_dict, prev_keys, original_data):
        if isinstance(select_op, list) and len(select_op) == 2:
            index, select_op = select_op[0], select_op[1]
        elif isinstance(select_op, dict) and len(select_op) == 1:
            index, select_op = list(select_op.items())[0]
        else:
            raise exceptions.IndexOperatorError
        if isinstance(index, list):
            if select_op in self.selection_operators:
                excl = lambda: self._index_excl_simple(index, selected_dict, prev_keys, original_data, data=data)
                incl = lambda: self._index_incl_simple(data, index, selected_dict, prev_keys)
                self._build_dict(
                    select_op, data, selected_dict, prev_keys, original_data, incl_func=incl, excl_func=excl
                )
                return
            values = []
            for i in index:
                try:
                    val = data[i]
                except IndexError:
                    continue
                except (TypeError, KeyError):
                    return
                if isinstance(val, dict):
                    val = self._select(val, select_op)
                    if not val and self._used == self.sel_include:
                        continue
                values.append((i, val))
            if not values:
                return
            incl = lambda: utils.set_from_list(selected_dict, prev_keys, [val[1] for val in values])
            excl = lambda: self._index_excl_multiple(data, values, selected_dict, prev_keys, original_data)
            self._build_dict(self._used, None, selected_dict, prev_keys, original_data, incl_func=incl, excl_func=excl)
            return
        try:
            value = self._operator_index(data, index)
        except (TypeError, IndexError, KeyError):
            return
        if select_op in self.selection_operators:
            excl = lambda: self._index_excl_simple(index, selected_dict, prev_keys, original_data, data=data)
            self._build_dict(select_op, value, selected_dict, prev_keys, original_data, excl_func=excl)
            return
        else:
            if not isinstance(value, dict):
                return
            value = self._select(value, select_op)
            if not value and self._used == self.sel_include:
                return
            excl = lambda: self._index_excl_nested(data, index, value, selected_dict, prev_keys, original_data)
        self._build_dict(self._used, value, selected_dict, prev_keys, original_data, excl_func=excl)

    def _index_excl_multiple(self, data, values, selected_dict, prev_keys, original_data):
        data = self._try_coerce_list(data)
        try:
            data_copy = copy(data)
        except TypeError:
            return
        for i, val in values:
            try:
                data_copy[i] = val
            except IndexError:
                continue
            except (KeyError, TypeError):
                return
        self._exclude(selected_dict, prev_keys, original_data, data_copy)

    @_copy_data
    def _index_excl_simple(self, index, selected_dict, prev_keys, original_data, data=None):
        values = self._try_coerce_list(data)
        index = [index] if not isinstance(index, list) else index
        try:
            for i in sorted(index, reverse=True):
                del values[i]
        except (TypeError, IndexError):
            return
        self._exclude(selected_dict, prev_keys, original_data, values)

    @staticmethod
    def _index_incl_simple(data, index, selected_dict, prev_keys):
        values = []
        try:
            for i in index:
                values.append(data[i])
        except (TypeError, IndexError, KeyError):
            return
        if values:
            utils.set_from_list(selected_dict, prev_keys, values)

    def _index_excl_nested(self, data, index, value, selected_dict, prev_keys, original_data):
        values = self._try_coerce_list(data)
        try:
            values[index] = value
        except TypeError:
            return
        self._exclude(selected_dict, prev_keys, original_data, values)

    def _operator_sel_range(self, data, select_op, selected_dict, prev_keys, original_data):
        if not isinstance(select_op, dict) or len(select_op) != 1:
            raise exceptions.RangeSelectionOperatorError
        range_str, select_op = list(select_op.items())[0]
        try:
            values = self._operator_range(data, range_str)
        except TypeError:
            return
        if select_op in self.selection_operators:
            func = lambda dt: exec(f"del data[{range_str}]", {"data": dt})
        else:
            values = self._select_iter(values, select_op)
            if not values:
                return
            func = lambda dt: exec(f"data[{range_str}] = values", {"data": dt, "values": values})
        excl = lambda: self._range_excl(selected_dict, prev_keys, original_data, func, data=data)
        self._build_dict(self._used or select_op, values, selected_dict, prev_keys, original_data, excl_func=excl)

    @_copy_data
    def _range_excl(self, selected_dict, prev_keys, original_data, func, data=None):
        data = self._try_coerce_list(data)
        try:
            func(data)
        except TypeError:
            return
        self._exclude(selected_dict, prev_keys, original_data, data)

    def _try_coerce_list(self, data):
        if self._coerce_list:
            try:
                return list(data)
            except TypeError:
                return
        return data

    @staticmethod
    def _exclude(selected_dict, prev_keys, original_data, values):
        if not selected_dict:
            selected_dict.update(original_data)
        utils.set_from_list(selected_dict, prev_keys, values)

    def _build_dict(self, operator, data, selected_dict, prev_keys, original_data, incl_func=None, excl_func=None):
        if not prev_keys:
            return
        if operator == self.sel_include:
            self._used = self.sel_include
            incl_func() if incl_func else utils.set_from_list(selected_dict, prev_keys, data)
        elif operator == self.sel_exclude:
            self._used = self.sel_exclude
            if excl_func:
                excl_func()
                return
            if not selected_dict:
                selected_dict.update(original_data)
            utils.pop_from_list(selected_dict, prev_keys)
