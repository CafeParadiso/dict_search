from collections import abc
import re
from typing import Type
from typing import Union

from . import exceptions
from . import low_level_operators as lop
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
        operator_str: str =None,
        low_level_custom_op: dict[str, Type[lop.LowLevelOperator]] = None,
        low_level_glob_exc: Type[Exception] = None,
        low_level_oper_exc: dict[
            Type[lop.LowLevelOperator], Union[Type[Exception], tuple[Type[Exception], ...], None]
        ] = None,
        low_level_glob_exc_val: bool = False,
        low_level_exc_value: dict = None,
        consumable_iterators=None,
        non_consumable_iterators=None,
        iterator_cast_type=list,
        coerce_list=False,
        sel_array_ignored_types=None,
    ):
        self.operator_str = operator_str if isinstance(operator_str, str) else "$"
        self.low_level_custom_op = low_level_custom_op or {}
        self.low_level_glob_exc = low_level_glob_exc
        self.low_level_oper_exc = low_level_oper_exc or {}
        self.low_level_glob_exc_val = low_level_glob_exc_val
        self.low_level_exc_value = low_level_exc_value or {}
        self._consumable_iterators = consumable_iterators
        self._non_consumable_iterators = non_consumable_iterators
        self._iterator_cast_type = iterator_cast_type
        self._coerce_list = coerce_list
        self.sel_array_ignored_types = sel_array_ignored_types
        self._empty = False

        # matching operators
        self.lop_ne = f"{self.operator_str}ne"
        self.lop_gt = f"{self.operator_str}gt"
        self.lop_gte = f"{self.operator_str}gte"
        self.lop_lt = f"{self.operator_str}lt"
        self.lop_lte = f"{self.operator_str}lte"
        self.lop_is = f"{self.operator_str}is"
        self.lop_in = f"{self.operator_str}in"
        self.lop_nin = f"{self.operator_str}nin"
        self.lop_cont = f"{self.operator_str}cont"
        self.lop_ncont = f"{self.operator_str}ncont"
        self.lop_regex = f"{self.operator_str}regex"
        self.lop_expr = f"{self.operator_str}expr"
        self.lop_inst = f"{self.operator_str}inst"
        self.lop_comp = f"{self.operator_str}comp"
        self._lop_map = {}
        self._lop_eq = None
        self._initial_data = {}
        self.low_level_operators = [val for key, val in self.__dict__.items() if re.match(r"^lop_.*$", key)]
        self._low_level_comparison_operators = [self.lop_ne, self.lop_gt, self.lop_gte, self.lop_lt, self.lop_lte]

        self.hop_and = f"{self.operator_str}and"
        self.hop_or = f"{self.operator_str}or"
        self.hop_not = f"{self.operator_str}not"
        self.high_level_operators = [val for key, val in self.__dict__.items() if re.match(r"^hop_.*$", key)]

        self.aop_all = f"{self.operator_str}all"
        self.aop_any = f"{self.operator_str}any"
        self.array_operators = [val for key, val in self.__dict__.items() if re.match(r"^aop_.*$", key)]

        self.mop_match = f"{self.operator_str}match"
        self.mop_matchgt = f"{self.operator_str}matchgt"
        self.mop_matchgte = f"{self.operator_str}matchgte"
        self.mop_matchlt = f"{self.operator_str}matchlt"
        self.mop_matchlte = f"{self.operator_str}matchlte"
        self.match_operators = [val for key, val in self.__dict__.items() if re.match(r"^mop_.*$", key)]

        self.as_index = f"{self.operator_str}index"
        self.as_range = f"{self.operator_str}range"
        self.as_where = f"{self.operator_str}where"
        self.array_selectors = [val for key, val in self.__dict__.items() if re.match(r"^as_.*$", key)]

        # select
        self.sel_include = 1
        self.sel_exclude = 0
        self._used = None
        self.selection_operators = [self.sel_include, self.sel_exclude]
        self.sel_array = f"{self.operator_str}array"

        self.set_low_level_ops()

    def __call__(self, data, match_dict=None, select_dict=None):
        data = [data] if isinstance(data, dict) else data
        if not all(not arg or isinstance(arg, dict) for arg in [match_dict, select_dict]):
            raise exceptions.PreconditionError()
        for data_point in data:
            if not isinstance(data_point, dict) or not data_point:
                continue
            self._initial_data = data_point
            if match_dict and not all(match for match in self._match(data_point, match_dict)):
                continue
            if select_dict:
                self._empty = False
                selected_dict = self._select(data_point, select_dict)
                if not selected_dict and not self._empty:
                    continue
                yield selected_dict
            else:
                yield data_point

    def _match(self, data, match_dict, prev_keys=None):
        prev_keys = prev_keys if prev_keys else []
        if isinstance(match_dict, dict) and match_dict:
            for key, value in match_dict.items():
                if key in self.low_level_operators:
                    yield self._low_level_operator(key, data, value)
                elif key in self.high_level_operators:
                    yield self._high_level_operator(key, data, value, prev_keys)
                elif key in self.array_operators:
                    yield self._array_operators(key, data, value, prev_keys)
                elif key in self.match_operators:
                    yield self._match_operators(key, data, value, prev_keys)
                elif key in self.array_selectors:
                    yield from self._match(*self._array_selector(key, data, value, prev_keys))
                elif not isinstance(data, dict) or isinstance(data, dict) and key not in data.keys():
                    yield False
                elif isinstance(value, dict):
                    prev_keys.append(key)
                    yield from self._match(data[key], value, prev_keys)
                    prev_keys.pop(-1)
                else:
                    yield self._lop_eq(data[key], value)
        else:
            yield self._lop_eq(data, match_dict)

    def _assign_consumed_iterator(self, data, prev_keys):
        if not self._consumable_iterators or not isinstance(data, self._consumable_iterators):
            return data
        if self._non_consumable_iterators and isinstance(data, self._non_consumable_iterators):
            return data
        data = self._iterator_cast_type.__call__(data)
        utils.set_from_list(self._initial_data, prev_keys, data)
        return data

    @staticmethod
    def _iscontainer(obj):
        if isinstance(obj, list):
            return True
        return False

    def set_low_level_ops(self):
        self._lop_map = {
            self.lop_ne: self._set_low_level_op(lop.NotEqual),
            self.lop_gt: self._set_low_level_op(lop.Greater),
            self.lop_gte: self._set_low_level_op(lop.GreaterEq),
            self.lop_lt: self._set_low_level_op(lop.LessThen),
            self.lop_lte: self._set_low_level_op(lop.LessThenEq),
            self.lop_is: self._set_low_level_op(lop.Is),
            self.lop_in: self._set_low_level_op(lop.In),
            self.lop_nin: self._set_low_level_op(lop.NotIn),
            self.lop_cont: self._set_low_level_op(lop.Contains),
            self.lop_ncont: self._set_low_level_op(lop.NotContains),
            self.lop_regex: self._set_low_level_op(lop.Regex),
            self.lop_expr: self._set_low_level_op(lop.Function),
            self.lop_inst: self._set_low_level_op(lop.IsInstance),
            self.lop_comp: self._set_low_level_op(lop.Compare),
            **{f"{self.operator_str}{k}": self._set_low_level_op(v) for k, v in self.low_level_custom_op.items()}
        }
        self._lop_eq = self._set_low_level_op(lop.Equal)

    def _set_low_level_op(self, operator_class):
        return operator_class(
            self,
            expected_exc=self.low_level_oper_exc[operator_class]
            if operator_class in self.low_level_oper_exc.keys()
            else self.low_level_glob_exc,
            exc_value=self.low_level_exc_value.get(operator_class) or self.low_level_glob_exc_val,
        )

    def _low_level_operator(self, operator, value, search_value):
        return self._lop_map[operator](value, search_value)

    def _high_level_operator(self, operator, data, search_container, prev_keys):
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
            match for search_dict in search_container for match in self._match(data, search_dict, prev_keys)
        )

    def _array_operators(self, operator, data, search_value, prev_keys):
        if not utils.isiter(data):
            return False
        data = self._assign_consumed_iterator(data, prev_keys)
        operator_map = {
            self.aop_all: self._operator_all,
            self.aop_any: self._operator_any,
        }
        return operator_map[operator](data, search_value, prev_keys)

    def _operator_all(self, data, search_value, prev_keys):
        if isinstance(search_value, dict):
            values = [match for d_point in data for match in self._match(d_point, search_value, prev_keys)]
        else:
            values = [self._lop_eq(d_point, search_value) for d_point in data]
        return False if not values else all(values)

    def _operator_any(self, data, search_value, prev_keys):
        if isinstance(search_value, dict):
            return any(match for d_point in data for match in self._match(d_point, search_value, prev_keys))
        return any(self._lop_eq(d_point, search_value) for d_point in data)

    def _match_operators(self, operator, data, search_value, prev_keys):
        try:
            thresh, search_value = list(search_value.items())[0]
        except (AttributeError, IndexError, AssertionError):
            raise exceptions.MatchOperatorError(search_value)
        if not isinstance(thresh, int):
            raise exceptions.MatchOperatorError(search_value)
        operator_map = {
            self.mop_match: [lambda m, c: True if m == c else False, lambda m, c: True if m > c else False, False],
            self.mop_matchgt: [lambda m, c: True if m > c else False, lambda m, c: True if m > c else False, True],
            self.mop_matchgte: [lambda m, c: True if m >= c else False, lambda m, c: True if m >= c else False, True],
            self.mop_matchlt: [lambda m, c: True if m < c else False, lambda m, c: True if m >= c else False, False],
            self.mop_matchlte: [lambda m, c: True if m <= c else False, lambda m, c: True if m > c else False, False],
        }
        default_args = operator_map[operator][0], thresh, operator_map[operator][1], operator_map[operator][2]

        if self._iscontainer(search_value):  # match is being used as high level operator
            return utils.shortcircuit_counter(
                iter(match for search_dict in search_value for match in self._match(data, search_dict, prev_keys)),
                *default_args,
            )
        data = self._assign_consumed_iterator(data, prev_keys)
        if isinstance(search_value, dict):  # match is being used as array operator
            return utils.shortcircuit_counter(
                iter(all([m for m in self._match(data_point, search_value, prev_keys)]) for data_point in data),
                *default_args,
            )
        return utils.shortcircuit_counter(  # match is being used as array op. to compare
            iter(self._lop_eq(d_point, search_value) for d_point in data), *default_args
        )

    def _array_selector(self, operator_type, data, search_value, prev_keys):
        if operator_type == self.as_where:
            return self._operator_where(data, search_value, prev_keys)
        elif operator_type == self.as_index and isinstance(search_value, list) and len(search_value) == 2:
            operator, search_value = search_value[0], search_value[1]
        elif isinstance(search_value, dict) and len(search_value):
            operator, search_value = list(search_value.items())[0]
        else:
            raise exceptions.ArraySelectorFormatException(operator_type)
        data = self._assign_consumed_iterator(data, prev_keys)
        try:
            return {self.as_index: self._operator_index, self.as_range: self._operator_range}[operator_type](
                data, operator
            ), search_value
        except (TypeError, IndexError, KeyError, ValueError):
            return [], {}

    def _operator_where(self, data, search_value, prev_keys):
        if not self._iscontainer(search_value) or len(search_value) != 2:
            raise exceptions.WhereOperatorError
        array_match_dict, match_dict = search_value
        data = self._assign_consumed_iterator(data, prev_keys)
        return [sub_dict for sub_dict in self(data, array_match_dict)], match_dict

    @staticmethod
    def _operator_index(data, index):
        if not isinstance(index, list):
            return data[index]
        values = []
        for i in index:
            try:
                values.append(data[i])
            except IndexError:
                continue
        if not values:
            raise ValueError
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
        if not isinstance(selection_dict, dict) or not data:
            return
        for key, val in selection_dict.items():
            if key == self.as_where and prev_keys and isinstance(data, abc.Iterable):
                self._operator_sel_where(data, val, selected_dict, prev_keys, original_data)
            elif key == self.as_index and prev_keys and isinstance(data, abc.Iterable):
                self._operator_sel_index(data, val, selected_dict, prev_keys, original_data)
            elif key == self.as_range and prev_keys and isinstance(data, abc.Iterable):
                self._operator_sel_range(data, val, selected_dict, prev_keys, original_data)
            elif key == self.sel_array and isinstance(data, abc.Iterable):
                if self.sel_array_ignored_types and isinstance(data, self.sel_array_ignored_types):
                    continue
                self._apply_to_container(data, selection_dict[key], selected_dict, prev_keys, original_data)
            elif not isinstance(data, dict) or key not in data.keys():
                continue
            elif val in self.selection_operators and isinstance(data, dict):
                prev_keys.append(key)
                self._build_dict(val, data[key], selected_dict, prev_keys, original_data)
                prev_keys.pop(-1)
            else:
                prev_keys.append(key)
                self._apply_selection(data[key], val, selected_dict, prev_keys, original_data)
                prev_keys.pop(-1)

    def _select_iter(self, data, selection_dict):
        values = []
        for d_point in data:
            if not isinstance(d_point, dict) or not d_point:
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
        data = self._assign_consumed_iterator(data, prev_keys)
        if len(data) == 0:
            return
        match_dict, operator = search_value
        if isinstance(operator, dict):
            self._apply_to_container(self(data, match_dict), operator, selected_dict, prev_keys, original_data)
        else:
            incl = lambda: self.where_incl(match_dict, selected_dict, data, prev_keys)
            excl = lambda: self.where_excl(match_dict, selected_dict, data, prev_keys, original_data)
            self._build_dict(operator, None, selected_dict, prev_keys, original_data, incl_func=incl, excl_func=excl)

    def where_incl(self, match_dict, selected_dict, data, prev_keys):
        values = [d_point for d_point in data if all(self._match(d_point, match_dict))]
        utils.set_from_list(selected_dict, prev_keys, values) if values else None

    def where_excl(self, match_dict, selected_dict, data, prev_keys, original_data):
        values = [d_point for d_point in data if not all(self._match(d_point, match_dict))]
        if values and values != data:
            self._exclude(selected_dict, prev_keys, original_data, values)

    def _operator_sel_index(self, data, select_op, selected_dict, prev_keys, original_data):
        if isinstance(select_op, list) and len(select_op) == 2:
            index, select_op = select_op[0], select_op[1]
        elif isinstance(select_op, dict) and len(select_op) == 1:
            index, select_op = list(select_op.items())[0]
        else:
            raise exceptions.IndexOperatorError
        data = self._assign_consumed_iterator(data, prev_keys)
        if len(data) == 0:
            return
        if select_op in self.selection_operators:
            value = None
            if select_op == self.sel_include:
                try:
                    value = self._operator_index(data, index)
                except (IndexError, TypeError, KeyError, ValueError):
                    return
            excl = lambda: self._index_excl_simple(index, selected_dict, prev_keys, original_data, data=data)
            self._build_dict(select_op, value, selected_dict, prev_keys, original_data, excl_func=excl)
            return
        index = [index] if not isinstance(index, list) else index
        values = []
        for i in index:
            try:
                val = data[i]
            except (TypeError, KeyError):
                return
            except IndexError:
                continue
            if not isinstance(val, dict):
                continue
            val = self._select(val, select_op)
            if not val and self._used == self.sel_include:
                continue
            values.append((i, val))
        if not values:
            return
        excl = lambda: self._index_excl_nested(values, selected_dict, prev_keys, original_data, data=data)
        incl = lambda: utils.set_from_list(
            selected_dict, prev_keys, values[0][1] if len(values) == 1 else [v[1] for v in values]
        )
        self._build_dict(self._used, None, selected_dict, prev_keys, original_data, incl_func=incl, excl_func=excl)

    @_copy_data
    def _index_excl_simple(self, index, selected_dict, prev_keys, original_data, data=None):
        values = self._try_coerce_list(data)
        index = [index] if not isinstance(index, list) else index
        for i in sorted(index, reverse=True):
            try:
                del values[i]
            except IndexError:
                continue
            except (TypeError, KeyError):
                return
        self._exclude(selected_dict, prev_keys, original_data, values)

    @_copy_data
    def _index_excl_nested(self, values, selected_dict, prev_keys, original_data, data=None):
        data = self._try_coerce_list(data)
        for i, val in values:
            try:
                data[i] = val
            except IndexError:
                continue
            except (KeyError, TypeError):
                return
        self._exclude(selected_dict, prev_keys, original_data, data)

    def _operator_sel_range(self, data, select_op, selected_dict, prev_keys, original_data):
        if not isinstance(select_op, dict) or len(select_op) != 1:
            raise exceptions.RangeSelectionOperatorError
        data = self._assign_consumed_iterator(data, prev_keys)
        if len(data) == 0:
            return
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
            if len(prev_keys) == 1 and len(selected_dict) == 1 and prev_keys[0] in selected_dict:
                self._empty = True
            utils.pop_from_list(selected_dict, prev_keys)
