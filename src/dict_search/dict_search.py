from collections import abc
from types import ModuleType
from typing import Type, Union

from . import constants as c
from . import exceptions
from . import utils
from .operators import ALL_OPERATOR_TYPES, Operator
from .operators import array_operators as aop
from .operators import array_selectors as asop
from .operators import count_operators as cop
from .operators import exceptions as op_exceptions
from .operators import get_operators
from .operators import high_level_operators as hop
from .operators import low_level_operators as lop
from .operators import match_operators as mop
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
        match_query: dict = None,
        select_query: dict = None,
        ops_str: str = None,
        ops_global_exc: Union[Type[Exception], tuple[..., Type[Exception]]] = None,
        ops_global_allowed_type: Union[Type[type], tuple[..., Type[type]]] = None,
        ops_global_ignored_type: Union[Type[type], tuple[..., Type[type]]] = None,
        ops_custom: Union[Type[Operator], list[..., Type[Operator]]] = None,
        ops_config: dict = None,
        container_type=list,
        consumable_iterators=None,
        non_consumable_iterators=None,
        cast_type_iterators=list,
        coerce_list=False,
        sel_array_ignored_types=None,
    ):
        # TODO set accessibility
        self.ops_str = ops_str if isinstance(ops_str, str) else "$"  # public - runtime setting -> recalculate
        self.ops_global_exc = ops_global_exc  # public - runtime setting -> recalculate ?
        self.ops_global_allowed_type = ops_global_allowed_type  # public - runtime setting -> recalculate ?
        self.ops_global_ignored_type = ops_global_ignored_type  # public - runtime setting -> recalculate ?
        self.container_type = container_type
        self.consumable_iterators = consumable_iterators
        self.non_consumable_iterators = non_consumable_iterators
        self.cast_type_iterators = cast_type_iterators  # public ?
        self._coerce_list = coerce_list  # public ?
        self.sel_array_ignored_types = sel_array_ignored_types  # public ?
        self._initial_data = {}

        self.all_match_ops = {}
        self.low_level_operators = self.__set_match_ops(lop)
        self.high_level_operators = self.__set_match_ops(hop)
        self.array_operators = self.__set_match_ops(aop)
        self.array_selectors = self.__set_match_ops(asop)
        self.count_operators = self.__set_match_ops(cop)
        self.match_operators = self.__set_match_ops(mop)

        # select attributes
        self.sel_array = f"{self.ops_str}array"
        self.sel_include = 1
        self.sel_exclude = 0
        self._empty = False
        self._used = None
        self.selection_operators = [self.sel_include, self.sel_exclude]

        # init steps
        self.__set_ops_custom(ops_custom or [])
        self._ops_config = self.__set_ops_config(ops_config or {})
        self._class_config_keys = set(filter(lambda x: x != Operator and not isinstance(x, str), self._ops_config))
        self.__init_operators()
        self.__set_ops_names_attrs()

        self.__inner_call__ = None
        self._call_layers = {
            self.__wrap_select: None,
            self.__wrap_match: None,
        }
        self.select_query = select_query
        self.match_query = match_query

    def __set_match_ops(self, ops_module: ModuleType):
        ops_names = []
        ops_classes = get_operators(ops_module)
        for op_class in ops_classes:
            op_name = f"{self.ops_str}{op_class.name}"
            self.all_match_ops[op_name] = op_class
            ops_names.append(op_name)
        return ops_names

    def __set_array_selectors(self, func):
        def wrapper(data, value, prev_keys, *args):
            value, match_dict = value[0], value[1]
            data = self._assign_consumed_iterator(data, prev_keys)
            return func(data, value, *args), match_dict
        return wrapper

    def __set_ops_custom(self, ops_custom: Union[Type[Operator], list[..., Type[Operator]]]):
        ops_custom = ops_custom if isinstance(ops_custom, list) else [ops_custom]
        for op in ops_custom:
            if not isinstance(op, type) or not issubclass(op, Operator):
                raise exceptions.CustomOpsValueError
            op_name = f"{self.ops_str}{op.name}"
            if op_name in self.all_match_ops:
                raise exceptions.CustomOpsExistingKey(op_name)
            self.all_match_ops[op_name] = op
            self.low_level_operators.append(op_name)

    def __set_ops_config(self, ops_config):
        parsed = {}
        for k, v in ops_config.items():
            if isinstance(k, str):
                k = f"{self.ops_str}{k}"
                if k not in self.all_match_ops:
                    raise exceptions.OpsConfigNonExistingKey(k, self.ops_str)
            elif not isinstance(k, type) or k not in ALL_OPERATOR_TYPES:
                raise exceptions.OpsConfigKeyError
            if not isinstance(v, dict) or not v or not all(key in c.LOP_CONF_KEYS for key in v):
                raise exceptions.OpsConfigValueError
            parsed[k] = v
        return parsed

    def __init_operators(self) -> None:
        for k, v in self.all_match_ops.items():
            op_instance = v(self.ops_global_exc, self.ops_global_allowed_type, self.ops_global_ignored_type)
            if Operator in self._ops_config:
                op_instance = self.__set_from_config(Operator, op_instance)
            base_class_config = tuple(filter(lambda x: issubclass(v.__base__, x), self._class_config_keys))
            if base_class_config:
                op_instance = self.__set_from_config(base_class_config[0], op_instance)
            if k in self._ops_config:
                op_instance = self.__set_from_config(k, op_instance)
            if k in self.array_selectors:
                op_instance.implementation = self.__set_array_selectors(op_instance.implementation)
            self.all_match_ops[k] = op_instance

    def __set_from_config(self, key, op_instance):
        op_instance.expected_exc = self._ops_config.get(key, {}).get(c.LOP_CONF_EXC, op_instance.expected_exc)
        op_instance.allowed_types = self._ops_config.get(key, {}).get(c.LOP_CONF_ALL_TYPE, op_instance.allowed_types)
        op_instance.ignored_types = self._ops_config.get(key, {}).get(c.LOP_CONF_IG_TYPE, op_instance.ignored_types)
        op_instance.default_return = self._ops_config.get(key, {}).get(c.LOP_CONF_DEF_RET, op_instance.default_return)
        return op_instance

    def __set_ops_names_attrs(self):
        for op_name, op_instance in self.all_match_ops.items():
            setattr(self, f"op__{op_instance.name}", op_name)

    def __set_query_dict(self, value, func):
        if value is None:
            self._call_layers[func] = None
        elif isinstance(value, dict):
            self._call_layers[func] = func
        else:
            raise exceptions.PreconditionError
        self.__layer_funcs()
        return value

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
        self._select_query = self.__set_query_dict(value, self.__wrap_select)
        if isinstance(value, dict):
            self.__parse_select_query(value)

    @property
    def match_query(self):
        return self._match_query

    def __wrap_match(self, func):
        def wrapper(data):
            if self._match(data, self.match_query):
                return func(data)

        return wrapper

    @match_query.setter
    def match_query(self, value):
        self._match_query = self.__set_query_dict(value, self.__wrap_match)
        if isinstance(value, dict):
            self.__parse_match_query(value)

    def __layer_funcs(self):
        self.__inner_call__ = lambda x: x
        for val in self._call_layers.values():
            if val:
                self.__inner_call__ = val(self.__inner_call__)

    def __call__(self, data):
        self._initial_data = data
        if isinstance(data, dict):
            return self.__inner_call__(data)

    def __parse_match_query(self, match_dict):
        for k, v in match_dict.items():
            if k in self.all_match_ops:
                self.all_match_ops[k].precondition(v)
            if isinstance(v, dict):
                self.__parse_match_query(v)
            elif isinstance(v, self.container_type):
                [self.__parse_match_query(d) for d in v if isinstance(d, dict)]

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

    def _assign_consumed_iterator(self, data, prev_keys):
        if not self.consumable_iterators or not isinstance(data, self.consumable_iterators):
            return data
        if self.non_consumable_iterators and isinstance(data, self.non_consumable_iterators):
            return data
        data = self.cast_type_iterators.__call__(data)
        utils.set_from_list(self._initial_data, prev_keys, data)
        return data

    def _match(self, data, match_query):
        if all(self._apply_match(data, match_query)):
            return data

    def _apply_match(self, data, match_dict, prev_keys=None):
        prev_keys = prev_keys if prev_keys else []
        if isinstance(match_dict, dict) and match_dict:
            for key, value in match_dict.items():
                if key == self.op__comp:
                    yield self.all_match_ops[key].implementation(data, value, self._initial_data)
                elif key == self.op__where:
                    yield from self._apply_match(*self.all_match_ops[key].implementation(data, value, prev_keys, self))
                elif key in self.low_level_operators:
                    yield self.all_match_ops[key].implementation(data, value)
                elif key in self.high_level_operators:
                    iterable = iter(
                        match
                        for search_dict in value
                        for match in self._apply_match(data, search_dict, prev_keys)
                    )
                    yield self.all_match_ops[key].implementation(iterable)
                elif key in self.match_operators:
                    thresh, search_value = list(value.items())[0]
                    iterable = iter(
                        all(self._apply_match(data, search_dict, prev_keys)) for search_dict in search_value
                    )
                    yield self.all_match_ops[key].implementation(iterable, thresh)
                elif key in self.array_operators:
                    data = self._assign_consumed_iterator(data, prev_keys)
                    iterable = iter(match for d_point in data for match in self._apply_match(d_point, value, prev_keys))
                    yield self.all_match_ops[key].implementation(iterable, value)
                elif key in self.count_operators:
                    thresh, search_value = list(value.items())[0]
                    iterable = iter(all(self._apply_match(data_point, search_value, prev_keys)) for data_point in data)
                    yield self.all_match_ops[key].implementation(thresh, iterable)
                elif key in self.array_selectors:
                    yield from self._apply_match(*self.all_match_ops[key].implementation(data, value, prev_keys))
                elif not isinstance(data, dict) or isinstance(data, dict) and key not in data.keys():
                    yield False
                elif isinstance(value, dict):
                    prev_keys.append(key)
                    yield from self._apply_match(data[key], value, prev_keys)
                    prev_keys.pop(-1)
                else:
                    yield self.all_match_ops[self.op__eq].implementation(data[key], value)
        else:
            yield self.all_match_ops[self.op__eq].implementation(data, match_dict)

    def _select(self, data, selection_dict):
        selected_dict = {}
        self._apply_selection(data, selection_dict, selected_dict)
        return selected_dict

    def _apply_selection(self, data, selection_dict, selected_dict, prev_keys=None, original_data=None):
        # TODO if not data:
        #   return
        prev_keys = prev_keys if prev_keys else []
        original_data = original_data if original_data else data.copy()
        if not isinstance(selection_dict, dict) or not data:  # TODO if not data:
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
        data = self._assign_consumed_iterator(data, prev_keys)
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
        data = self._assign_consumed_iterator(data, prev_keys)
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
        data = self._assign_consumed_iterator(data, prev_keys)
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
