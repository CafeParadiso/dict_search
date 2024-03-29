from pprint import pprint
from copy import deepcopy
from collections import abc
from types import ModuleType
from typing import Type, Union, Callable

from . import exceptions
from . import utils
from .operators import Operator
from .operators import exceptions as op_exceptions
from .operators import get_operators
from .operators.operators import (
    low_level_operators as lop,
    high_level_operators as hop,
    array_operators as aop,
    array_selectors as asop,
    count_operators as cop,
    match_operators as mop,
)


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
    def __assign_consumed_iterator(self, data, prev_keys):
        if not self.consumable_iterators or not isinstance(data, self.consumable_iterators):
            return data
        if self.non_consumable_iterators and isinstance(data, self.non_consumable_iterators):
            return data
        data = self.consumable_cast_type.__call__(data)
        utils.set_from_list(self._initial_data, prev_keys, data)
        return data

    def __init__(
        self,
        # *,
        match_query: dict = None,
        select_query: dict = None,
        ops_str: str = "$",
        ops_custom: Union[Type[Operator], list[..., Type[Operator]]] = None,
        ops_init_config: dict = None,
        container_type: Type = list,
        consumable_iterators=None,
        non_consumable_iterators=None,
        consumable_cast_type=list,
        coerce_list=False,
        sel_array_ignored_types=None,
    ):
        self.ops_str = ops_str
        self.container_type = container_type
        self.consumable_iterators = consumable_iterators
        self.non_consumable_iterators = non_consumable_iterators
        self.consumable_cast_type = consumable_cast_type
        self.coerce_list = coerce_list
        self.sel_array_ignored_types = sel_array_ignored_types
        self._initial_data = {}

        self.all_match_ops: dict[str, Type[Operator]] = {}
        self.__wrapped_ops: dict[str, Callable] = {}
        self.low_level_operators = self._load_ops_from_module(lop)
        self.high_level_operators = self._load_ops_from_module(hop, self.__wrap_high_level_op_impl)
        self.array_operators = self._load_ops_from_module(aop, self.__wrap_array_ops_impl)
        self.array_selectors = self._load_ops_from_module(asop, self.__wrap_array_selectors_impl)
        self.count_operators = self._load_ops_from_module(cop, self.__wrap_count_ops_impl)
        self.match_operators = self._load_ops_from_module(mop, self.__wrap_match_ops_impl)
        self.__set_ops_custom(ops_custom or [])
        self.__set_ops_names_attrs()
        self.used_operators = []

        # select attributes
        self.sel_array = f"{self.ops_str}array"
        self.sel_include = 1
        self.sel_exclude = 0
        self._empty = False
        self._used = None
        self.selection_operators = [self.sel_include, self.sel_exclude]

        self.ops_init_config = self.__parse_ops_init_config(ops_init_config or {})
        self.__inner_call__ = lambda x: x
        self._call_layers: dict = {
            self.__wrap_select: None,
            self.__wrap_match: None,
        }
        self.inner_eq_op = self.__configure_operator(self.op__eq, lop.Equal(None))
        self.match_query_parsed: dict = {}
        self.match_query: dict = match_query
        self.select_query: dict = select_query

    def _load_ops_from_module(self, ops_module: ModuleType, wrapper: Callable = None) -> list[str]:
        op_names = []
        for op_class in get_operators(ops_module):
            op_name = self.__build_op_name(op_class.name)
            if op_name in self.all_match_ops:
                raise exceptions.LoadOpsError(self.all_match_ops[op_name], op_name, op_class, ops_module)
            self.all_match_ops[op_name] = op_class
            op_names.append(op_name)
            if wrapper:
                self.__wrapped_ops[op_name] = wrapper
        return op_names

    def __build_op_name(self, op_name: str) -> str:
        return f"{self.ops_str}{op_name}"

    def __set_ops_custom(self, ops_custom: Union[Type[Operator], list[..., Type[Operator]]]):
        ops_custom = ops_custom if isinstance(ops_custom, list) else [ops_custom]
        for op in ops_custom:
            if not isinstance(op, type) or not issubclass(op, Operator):
                raise exceptions.CustomOpsValueError
            op_name = self.__build_op_name(op.name)
            if op_name in self.all_match_ops:
                raise exceptions.CustomOpsExistingKey(op_name)
            self.all_match_ops[op_name] = op
            self.low_level_operators.append(op_name)

    def __set_ops_names_attrs(self):
        for op_name, op_class in self.all_match_ops.items():
            setattr(self, f"op__{op_class.name}", op_name)

    def __parse_ops_init_config(self, config: dict):
        return {self.__build_op_name(k) if isinstance(k, str) else k: v for k, v in config.items()}

    def __call__(self, data) -> Union[dict, None]:
        self._initial_data = data
        if isinstance(data, dict):
            return self.__inner_call__(data)

    def filter(self, data: abc.Collection):
        """Return a filter object with only the valid members of the passed Collection"""
        return filter(lambda x: x is not None, map(self, data))

    def __set_call_layer(self, value, func):
        if value is None:
            self._call_layers[func] = None
        elif isinstance(value, dict):
            self._call_layers[func] = func
        else:
            raise exceptions.PreconditionError
        self.__layer_funcs()
        return value

    def __layer_funcs(self):
        self.__inner_call__ = lambda x: x
        for val in self._call_layers.values():
            if val:
                self.__inner_call__ = val(self.__inner_call__)

    def get_operator(self, name: str, filter_dict: dict = None, first=True) -> Union[Operator, list]:
        operators = [op for op in self.used_operators if op.name == name]
        if filter_dict:
            operators = [op for op in operators if all(getattr(op, k) == v for k, v in filter_dict.items())]
        if operators:
            return operators[0] if first else operators

    @property
    def match_query(self):
        return self._match_query

    @match_query.setter
    def match_query(self, value):
        self._match_query = self.__set_call_layer(value, self.__wrap_match)
        if value:
            self.match_query_parsed = self._parse_match_query(deepcopy(value))

    def __wrap_match(self, func):
        def wrapper(data):
            if self._match(data, self.match_query_parsed):
                return func(data)

        return wrapper

    def _parse_match_query(self, match_query, parsed_match_query=None):
        parsed_match_query = {} if not parsed_match_query else parsed_match_query
        for k, v in match_query.items():
            if k in self.all_match_ops:
                node = self.all_match_ops[k].init_match_node(v, self._parse_match_query)
                node.operator = self.__configure_operator(k, node.operator)
                parsed_match_query[k] = node
                self.used_operators.append(node.operator)
            elif isinstance(v, dict):
                parsed_match_query[k] = v
                self._parse_match_query(v, parsed_match_query[k])
            else:
                node = self.all_match_ops[self.op__eq].init_match_node(v)
                self.__configure_operator(k, node.operator)
                parsed_match_query[k] = node
                self.used_operators.append(node.operator)
        return parsed_match_query

    def __configure_operator(self, op_name, op_instance: Operator) -> Operator:
        if op_name in self.__wrapped_ops:
            op_instance.implementation = self.__wrapped_ops[op_name](op_instance.implementation)
            op_instance.original_implementation = op_instance.implementation
        self.__set_from_config(op_name, op_instance)
        return op_instance

    def __set_from_config(self, op_name: dict, op_instance: Operator):
        for cls in reversed(list(filter(lambda x: x in self.ops_init_config, op_instance.__class__.mro()))):
            self.__set_config_attr(op_instance, self.ops_init_config[cls], cls)
        if op_name in self.ops_init_config:
            self.__set_config_attr(op_instance, self.ops_init_config[op_name], op_name)

    @staticmethod
    def __set_config_attr(op_instance: Operator, config_value: dict, config_key):
        for k, v in config_value.items():
            if hasattr(op_instance, k):
                setattr(op_instance, k, v)
            else:
                raise exceptions.OpsConfigKeyError(k, op_instance.name, config_key)

    def _match(self, data, match_query):
        if all(self._apply_match(data, match_query)):
            return data

    def _apply_match(self, data, match_dict, prev_keys=None):
        prev_keys = prev_keys if prev_keys else []
        if isinstance(match_dict, dict) and match_dict:
            for key, node in match_dict.items():
                if key == self.op__comp:
                    yield node.operator.implementation(data, self._initial_data)
                elif key == self.op__find:
                    yield from self._apply_match(node.operator(data), node.query, prev_keys)
                elif key == self.op__where:
                    yield from self._apply_match(node.operator.implementation(data, prev_keys, self), node.query)
                elif key in self.low_level_operators:
                    yield node.operator.implementation(data)
                elif (
                    key
                    in self.high_level_operators + self.match_operators + self.array_operators + self.count_operators
                ):
                    yield node.operator.implementation(data, node.query, prev_keys)
                elif key in self.array_selectors:
                    yield from self._apply_match(node.operator.implementation(data, prev_keys), node.query)
                elif not isinstance(data, dict) or isinstance(data, dict) and key not in data.keys():
                    yield False
                elif isinstance(node, dict):
                    prev_keys.append(key)
                    yield from self._apply_match(data[key], node, prev_keys)
                    prev_keys.pop(-1)
                else:
                    yield node.operator.implementation(data[key])
        else:
            self.inner_eq_op.comp = match_dict
            yield self.inner_eq_op.implementation(data)

    def __wrap_high_level_op_impl(self, func):
        def wrapper(data, value, prev_keys):
            iterable = iter(all(self._apply_match(data, search_dict, prev_keys)) for search_dict in value)
            return func(iterable)

        return wrapper

    def __wrap_match_ops_impl(self, func):
        def wrapper(data, match_query, prev_keys):
            iterable = iter(all(self._apply_match(data, search_dict, prev_keys)) for search_dict in match_query)
            return func(iterable)

        return wrapper

    def __wrap_array_ops_impl(self, func):
        def wrapper(data, value, prev_keys):
            if not isinstance(data, abc.Iterable) or not data:
                return False
            data = self.__assign_consumed_iterator(data, prev_keys)
            iterable = iter(all(self._apply_match(d_point, value, prev_keys)) for d_point in data)
            return func(iterable)

        return wrapper

    def __wrap_count_ops_impl(self, func):
        def wrapper(data, match_query, prev_keys):
            if not isinstance(data, abc.Iterable) or not data:
                return False
            data = self.__assign_consumed_iterator(data, prev_keys)
            iterable = iter(all(self._apply_match(data_point, match_query, prev_keys)) for data_point in data)
            return func(iterable)

        return wrapper

    def __wrap_array_selectors_impl(self, func):
        def wrapper(data, prev_keys, *args):
            data = self.__assign_consumed_iterator(data, prev_keys)
            return func(data, *args)

        return wrapper

    def _select(self, data, selection_dict):
        selected_dict = {}
        self._apply_selection(data, selection_dict, selected_dict)
        return selected_dict

    @property
    def select_query(self):
        return self._select_query

    def __wrap_select(self, func):
        def wrapper(data):
            self._empty = False
            result = self._select(data, self.select_query)
            if result or self._empty:
                return func(result)

        return wrapper

    @select_query.setter
    def select_query(self, value):
        self._used = None
        self._select_query = self.__set_call_layer(value, self.__wrap_select)
        if isinstance(value, dict):
            self.__parse_select_query(value)

    def __parse_select_query(self, select_query):
        for k, v in select_query.items():
            if k in self.all_match_ops:
                pass
            elif isinstance(v, dict):
                self.__parse_select_query(v)
            else:
                if v not in [self.sel_include, self.sel_exclude]:
                    raise exceptions.SelectValueError
                if self._used is None:
                    self._used = v
                elif self._used != v:
                    raise exceptions.SelectMixedError

    def _apply_selection(self, data, selection_dict, selected_dict, prev_keys=None, original_data=None):
        prev_keys = prev_keys if prev_keys else []
        original_data = original_data if original_data else data.copy()
        if not isinstance(selection_dict, dict) or not data:
            return
        for key, val in selection_dict.items():
            if key == self.op__where and prev_keys and isinstance(data, abc.Iterable):
                self._operator_sel_where(data, val, selected_dict, prev_keys, original_data)
            elif key == self.op__index and prev_keys and isinstance(data, abc.Iterable):
                self._operator_sel_index(data, val, selected_dict, prev_keys, original_data)
            elif key == self.op__slice and prev_keys and isinstance(data, abc.Iterable):
                self._operator_sel_slice(data, val, selected_dict, prev_keys, original_data)
            elif key == self.sel_array and isinstance(data, abc.Iterable):
                if self.sel_array_ignored_types and isinstance(data, self.sel_array_ignored_types):
                    continue
                self._apply_to_container(data, selection_dict[key], selected_dict, prev_keys, original_data)
            elif not isinstance(data, dict) or key not in data:
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
            raise op_exceptions.WhereOperatorError
        data = self.__assign_consumed_iterator(data, prev_keys)
        if len(data) == 0:
            return
        match_dict, operator = search_value
        if isinstance(operator, dict):
            values = [d_point for d_point in data if self._match(d_point, match_dict) is not None]
            self._apply_to_container(values, operator, selected_dict, prev_keys, original_data)
        else:
            incl = lambda: self.where_incl(match_dict, selected_dict, data, prev_keys)
            excl = lambda: self.where_excl(match_dict, selected_dict, data, prev_keys, original_data)
            self._build_dict(operator, None, selected_dict, prev_keys, original_data, incl_func=incl, excl_func=excl)

    def where_incl(self, match_dict, selected_dict, data, prev_keys):
        values = [d_point for d_point in data if self._match(d_point, match_dict) is not None]
        utils.set_from_list(selected_dict, prev_keys, values) if values else None

    def where_excl(self, match_dict, selected_dict, data, prev_keys, original_data):
        values = [d_point for d_point in data if not self._match(d_point, match_dict) is not None]
        if values and values != data:
            self._exclude(selected_dict, prev_keys, original_data, values)

    def _operator_sel_index(self, data, select_op, selected_dict, prev_keys, original_data):
        if isinstance(select_op, list) and len(select_op) == 2:
            index, select_op = select_op[0], select_op[1]
        elif isinstance(select_op, dict) and len(select_op) == 1:
            index, select_op = list(select_op.items())[0]
        else:
            raise op_exceptions.IndexOperatorError
        data = self.__assign_consumed_iterator(data, prev_keys)
        if len(data) == 0:
            return
        if select_op in self.selection_operators:
            value = None
            if select_op == self.sel_include:
                value = self.all_match_ops[self.op__index].implementation(data, (index, {}), prev_keys)[0]
                if value == []:  # TODO think how to signal empty value empty
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

    def _operator_sel_slice(self, data, select_op, selected_dict, prev_keys, original_data):
        data = self.__assign_consumed_iterator(data, prev_keys)
        if len(data) == 0:
            return
        slice_str, select_op = list(select_op.items())[0]
        values = self.all_match_ops[self.op__slice].implementation(data, (slice_str, {}), prev_keys)[0]
        if values == []:
            return
        if select_op in self.selection_operators:
            func = lambda dt: exec(f"del data[{slice_str}]", {"data": dt})
        else:
            values = self._select_iter(values, select_op)
            if not values:
                return
            func = lambda dt: exec(f"data[{slice_str}] = values", {"data": dt, "values": values})
        excl = lambda: self._slice_excl(selected_dict, prev_keys, original_data, func, data=data)
        self._build_dict(self._used or select_op, values, selected_dict, prev_keys, original_data, excl_func=excl)

    @_copy_data
    def _slice_excl(self, selected_dict, prev_keys, original_data, func, data=None):
        data = self._try_coerce_list(data)
        try:
            func(data)
        except TypeError:
            return
        self._exclude(selected_dict, prev_keys, original_data, data)

    def _try_coerce_list(self, data):
        if self.coerce_list:
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
