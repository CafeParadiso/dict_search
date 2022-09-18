from collections import abc
from types import ModuleType
from typing import Type, Union

from . import constants as c
from . import exceptions
from . import utils
from .operators import ALL_OPERATOR_TYPES, Operator
from .operators import array_operators as aop
from .operators import array_selectors as asop
from .operators import exceptions as op_exceptions
from .operators import get_operators
from .operators import high_level_operators as hop
from .operators import low_level_operators as lop
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
        ops_str: str = None,
        ops_global_exc: Union[Type[Exception], tuple[..., Type[Exception]]] = None,
        ops_global_allowed_type: Union[Type[type], tuple[..., Type[type]]] = None,
        ops_global_ignored_type: Union[Type[type], tuple[..., Type[type]]] = None,
        ops_custom: dict[str, Type[Operator]] = None,
        ops_config: dict = None,
        container_type=list,
        consumable_iterators=None,
        non_consumable_iterators=None,
        iterator_cast_type=list,
        coerce_list=False,
        sel_array_ignored_types=None,
    ):
        self.ops_str = ops_str if isinstance(ops_str, str) else "$"
        self.ops_global_exc = ops_global_exc
        self.ops_global_allowed_type = ops_global_allowed_type
        self.ops_global_ignored_type = ops_global_ignored_type
        self.container_type = container_type
        self._consumable_iterators = consumable_iterators
        self._non_consumable_iterators = non_consumable_iterators
        self._iterator_cast_type = iterator_cast_type
        self._coerce_list = coerce_list
        self.sel_array_ignored_types = sel_array_ignored_types
        self._initial_data = {}

        self.all_match_ops = {}
        self.low_level_operators = self.__set_match_ops(lop)
        self.high_level_operators = self.__set_match_ops(hop)
        self.array_operators = self.__set_match_ops(aop)
        self.array_selectors = self.__set_match_ops(asop)

        # select attributes
        self.sel_array = f"{self.ops_str}array"
        self.sel_include = 1
        self.sel_exclude = 0
        self._empty = False
        self._used = None
        self.selection_operators = [self.sel_include, self.sel_exclude]

        # init steps
        self.ops_custom = self.__set_ops_custom(ops_custom or {})
        self.ops_config = self.__set_ops_config(ops_config or {})
        self._class_config_keys = set(filter(lambda x: x != Operator and not isinstance(x, str), self.ops_config))
        self.__init_operators()
        self.__set_ops_names_attrs()

    def __set_match_ops(self, ops_module: ModuleType):
        ops_names = []
        ops_classes = get_operators(ops_module)
        for op_class in ops_classes:
            op_name = f"{self.ops_str}{op_class.name}"
            self.all_match_ops[op_name] = op_class
            ops_names.append(op_name)
        return ops_names

    def __set_ops_custom(self, value: dict):
        parsed = {}
        for k, v in value.items():
            if not isinstance(k, str):
                raise exceptions.CustomOpsKeyError(self.ops_str)
            custom_op = f"{self.ops_str}{k}"
            if custom_op in self.all_match_ops:
                raise exceptions.CustomOpsExistingKey(custom_op)
            if not isinstance(v, type) or not issubclass(v, Operator):
                raise exceptions.CustomOpsValueError
            parsed[custom_op] = v
        self.low_level_operators.extend(parsed)
        self.all_match_ops.update(parsed)
        return parsed

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

    def __set_ops_names_attrs(self):
        for op_name, op_instance in self.all_match_ops.items():
            setattr(self, f"op_{op_instance.name}", op_name)

    def __init_operators(self) -> None:
        for k, v in self.all_match_ops.items():
            op_instance = v(self, self.ops_global_exc, self.ops_global_allowed_type, self.ops_global_ignored_type)
            if Operator in self.ops_config:
                op_instance = self.__init_from_config(Operator, v, op_instance)
            base_class_config = tuple(filter(lambda x: issubclass(v.__base__, x), self._class_config_keys))
            if base_class_config:
                op_instance = self.__init_from_config(base_class_config[0], v, op_instance)
            if k in self.ops_config:
                op_instance = self.__init_from_config(k, v, op_instance)
            self.all_match_ops[k] = op_instance

    def __init_from_config(self, key, op_class, op_instance):
        return op_class(
            self,
            expected_exc=self.ops_config.get(key, {}).get(c.LOP_CONF_EXC, op_instance.expected_exc),
            allowed_types=self.ops_config.get(key, {}).get(c.LOP_CONF_ALL_TYPE, op_instance.allowed_types),
            ignored_types=self.ops_config.get(key, {}).get(c.LOP_CONF_IG_TYPE, op_instance.ignored_types),
            default_return=self.ops_config.get(key, {}).get(c.LOP_CONF_DEF_RET, op_instance.default_return),
        )

    def __call__(self, data, match_dict=None, select_dict=None):
        data = [data] if isinstance(data, dict) else data
        if not all(not arg or isinstance(arg, dict) for arg in [match_dict, select_dict]):
            raise exceptions.PreconditionError
        if match_dict:
            self.__parse_match_dict(match_dict)
        for data_point in data:
            if not isinstance(data_point, dict) or not data_point:
                continue
            self._initial_data = data_point
            if match_dict and not all(self._match(data_point, match_dict)):
                continue
            result = data_point
            if select_dict:
                self._empty = False
                result = self._select(data_point, select_dict)
                if not result and not self._empty:
                    continue
            yield result

    def __parse_match_dict(self, match_dict):
        for k, v in match_dict.items():
            if k in self.all_match_ops:
                self.all_match_ops[k].precondition(v)
            if isinstance(v, dict):
                self.__parse_match_dict(v)
            elif isinstance(v, self.container_type):
                [self.__parse_match_dict(d) for d in v if isinstance(d, dict)]

    def _assign_consumed_iterator(self, data, prev_keys):
        if not self._consumable_iterators or not isinstance(data, self._consumable_iterators):
            return data
        if self._non_consumable_iterators and isinstance(data, self._non_consumable_iterators):
            return data
        data = self._iterator_cast_type.__call__(data)
        utils.set_from_list(self._initial_data, prev_keys, data)
        return data

    def _match(self, data, match_dict, prev_keys=None):
        prev_keys = prev_keys if prev_keys else []
        if isinstance(match_dict, dict) and match_dict:
            for key, value in match_dict.items():
                if key in self.low_level_operators:
                    yield self.all_match_ops[key](data, value)
                elif key in self.high_level_operators:
                    yield self.all_match_ops[key](data, value, prev_keys)
                elif key in self.array_operators:
                    yield self.all_match_ops[key](data, value, prev_keys)
                elif key in self.array_selectors:
                    yield from self._match(*self.all_match_ops[key](data, value, prev_keys))
                elif not isinstance(data, dict) or isinstance(data, dict) and key not in data.keys():
                    yield False
                elif isinstance(value, dict):
                    prev_keys.append(key)
                    yield from self._match(data[key], value, prev_keys)
                    prev_keys.pop(-1)
                else:
                    yield self.all_match_ops[self.op_eq](data[key], value)
        else:
            yield self.all_match_ops[self.op_eq](data, match_dict)

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
            if key == self.op_where and prev_keys and isinstance(data, abc.Iterable):
                self._operator_sel_where(data, val, selected_dict, prev_keys, original_data)
            elif key == self.op_index and prev_keys and isinstance(data, abc.Iterable):
                self._operator_sel_index(data, val, selected_dict, prev_keys, original_data)
            elif key == self.op_range and prev_keys and isinstance(data, abc.Iterable):
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
            raise op_exceptions.WhereOperatorError
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
            raise op_exceptions.IndexOperatorError
        data = self._assign_consumed_iterator(data, prev_keys)
        if len(data) == 0:
            return
        if select_op in self.selection_operators:
            value = None
            if select_op == self.sel_include:
                value, empty = self.all_match_ops[self.op_index].implementation(data, index, None)
                if empty == {}:
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
        data = self._assign_consumed_iterator(data, prev_keys)
        if len(data) == 0:
            return
        range_str, select_op = list(select_op.items())[0]
        values, empty = self.all_match_ops[self.op_range].implementation(data, range_str, None)
        if empty == {}:
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
