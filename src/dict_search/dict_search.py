from collections import abc
import re

from . import constants
from . import exceptions
from pprint import pprint


class DictSearch:
    def __init__(self, operator_str=None):
        self.operator_char = operator_str if isinstance(operator_str, str) else None or "$"

        # matching operators
        self.lop_ne = f"{self.operator_char}ne"
        self.lop_gt = f"{self.operator_char}gt"
        self.lop_gte = f"{self.operator_char}gte"
        self.lop_lt = f"{self.operator_char}lt"
        self.lop_lte = f"{self.operator_char}lte"
        self.lop_in = f"{self.operator_char}in"
        self.lop_nin = f"{self.operator_char}nin"
        self.lop_cont = f"{self.operator_char}cont"
        self.lop_regex = f"{self.operator_char}regex"
        self.lop_expr = f"{self.operator_char}expr"
        self.lop_inst = f"{self.operator_char}inst"
        self.low_level_operators = [val for key, val in self.__dict__.items() if re.match(r"^lop_.*$", key)]

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

        self.sel_index = f"{self.operator_char}index"
        self.sel_range = f"{self.operator_char}range"
        self.sel_where = f"{self.operator_char}where"
        self.array_selectors = [val for key, val in self.__dict__.items() if re.match(r"^sel_.*$", key)]
        self._array_operator_map = {
            self.sel_index: self._operator_index,
            self.sel_range: self._operator_range,
            self.sel_where: self._operator_where,
        }

    @staticmethod
    def _isiter(data):
        try:
            iter(data)
            return True
        except TypeError:
            return False

    @staticmethod
    def _iscontainer(data):
        if isinstance(data, (abc.Container, abc.Generator)) and not isinstance(data, abc.Mapping):
            return True
        return False

    @staticmethod
    def _shortcircuit_counter(generator, counter, eager_check, eager_value, check):
        matches = 0
        for match in generator:
            if match:
                matches += 1
                if eager_check(matches, counter):
                    return eager_value
        return check(matches, counter)

    @staticmethod
    def _compare(data, search_value):
        """Some objects like numpy.Series will raise ValueError when evaluated for truth"""
        try:
            return data == search_value
        except ValueError:
            return False

    def dict_search(self, data, search_dict, select_dict=None):
        self._search_precondition(data, search_dict)
        for data_point in data:
            if isinstance(data_point, dict):
                if all(match for match in self._search(data_point, search_dict)):
                    if select_dict:
                        yield from self._select(data_point, select_dict)
                    else:
                        yield data_point

    def _search_precondition(self, data, search_dict):
        if not self._isiter(data):
            raise exceptions.PreconditionDataError(data)
        if not isinstance(search_dict, dict):
            raise exceptions.PreconditionSearchDictError(search_dict)

    def _search(self, data, search_dict):
        if isinstance(search_dict, dict) and search_dict:
            for key, value in search_dict.items():
                if key in self.low_level_operators:
                    yield self._low_level_operator(key, data, value)
                elif key in self.high_level_operators:
                    yield self._high_level_operator(key, data, search_dict[key])
                elif key in self.array_operators:
                    yield self._array_operators(key, data, value)
                elif key in self.match_operators:
                    yield self._match_operators(key, data, value)
                elif key in self.array_selectors:
                    yield from self._search(*self._array_selector(key, data, value))
                elif all(isinstance(obj, dict) for obj in [value, data]):
                    yield from self._search(data.get(key), value)
                elif isinstance(data, dict):
                    yield self._compare(data.get(key), value)
        else:
            yield False

    def _low_level_operator(self, operator, value, search_value):
        operation_map = {
            self.lop_ne: lambda val, search_val: val != search_val,
            self.lop_gt: lambda val, search_val: val > search_val,
            self.lop_gte: lambda val, search_val: val >= search_val,
            self.lop_lt: lambda val, search_val: val < search_val,
            self.lop_lte: lambda val, search_val: val <= search_val,
            self.lop_in: lambda val, search_val: val in search_val,
            self.lop_nin: lambda val, search_val: val not in search_val,
            self.lop_cont: lambda val, search_val: search_val in val,
            self.lop_regex: lambda val, search_patt: True if re.compile(search_patt).search(val) else False,
            self.lop_expr: lambda val, func: func(val) if isinstance(func(val), bool) else False,
            self.lop_inst: lambda val, search_type: isinstance(val, search_type),
        }
        try:
            return operation_map[operator](value, search_value)
        except TypeError:
            return False

    def _high_level_operator(self, operator, data, search_iterator):
        if not self._iscontainer(search_iterator):
            raise exceptions.HighLevelOperatorIteratorError
        operator_map = {
            self.hop_and: lambda matches: all(matches),
            self.hop_or: lambda matches: any(matches),
            self.hop_not: lambda matches: not all(matches),
        }
        return operator_map[operator](
            match for search_dict in search_iterator for match in self._search(data, search_dict)
        )

    def _array_operators(self, operator, data, search_value):
        if not self._isiter(data):
            return False
        operator_map = {
            self.aop_all: self._operator_all,
            self.aop_any: self._operator_any,
        }
        return operator_map[operator](data, search_value)

    def _operator_all(self, data, search_value):
        if isinstance(search_value, dict):
            return all(match for d_point in data for match in self._search(d_point, search_value))
        else:
            return all(self._compare(d_point, search_value) for d_point in data)

    def _operator_any(self, data, search_value):
        if isinstance(search_value, dict):
            return any(match for d_point in data for match in self._search(d_point, search_value))
        return any(self._compare(d_point, search_value) for d_point in data)

    def _match_operators(self, operator, data, search_value):
        try:
            count, search_value = list(search_value.items())[0]
        except AttributeError:
            return False
        try:
            count = int(count)
        except (TypeError, ValueError):
            return False
        operator_map = {
            self.mop_match: [lambda m, c: True if m > c else False, False, lambda m, c: True if m == c else False],
            self.mop_matchgt: [lambda m, c: True if m > c else False, True, lambda m, c: True if m > c else False],
            self.mop_matchgte: [lambda m, c: True if m >= c else False, True, lambda m, c: True if m >= c else False],
            self.mop_matchlt: [lambda m, c: True if m >= c else False, False, lambda m, c: True if m < c else False],
            self.mop_matchlte: [lambda m, c: True if m > c else False, False, lambda m, c: True if m <= c else False],
        }
        default_args = count, operator_map[operator][0], operator_map[operator][1], operator_map[operator][2]

        if self._iscontainer(search_value):  # match is being used as high level operator
            return self._shortcircuit_counter(
                iter(match for search_dict in search_value for match in self._search(data, search_dict)), *default_args
            )
        elif isinstance(search_value, dict):  # match is being used as array operator
            return self._shortcircuit_counter(
                iter(all([m for m in self._search(data_point, search_value)]) for data_point in data), *default_args
            )
        return self._shortcircuit_counter(  # match is being used as array operator to compare
            iter(self._compare(d_point, search_value) for d_point in data), *default_args
        )

    def _array_selector(self, operator_type, data, search_value):
        try:
            operator, search_value = list(search_value.items())[0]
        except AttributeError:
            return [], {}
        try:
            return self._array_operator_map[operator_type](data, search_value, operator)
        except (TypeError, IndexError):
            return [], {}

    @staticmethod
    def _operator_index(data, search_value, index):
        return data[int(index)], search_value

    @staticmethod
    def _operator_range(data, search_value, range_str):
        s, e, st = constants.S, constants.E, constants.ST
        range_map = {
            constants.RE_RANGE_S: lambda mtch_dict, dta: dta[int(mtch_dict[s]):],
            constants.RE_RANGE_E: lambda mtch_dict, dta: dta[:int(mtch_dict[e])],
            constants.RE_RANGE_ST: lambda mtch_dict, dta: dta[::int(mtch_dict[st])],
            constants.RE_RANGE_SE: lambda mtch_dict, dta: dta[int(mtch_dict[s]):int(mtch_dict[e])],
            constants.RE_RANGE_SST: lambda mtch_dict, dta: dta[int(mtch_dict[s])::int(mtch_dict[st])],
            constants.RE_RANGE_EST: lambda mtch_dict, dta: dta[:int(mtch_dict[e]):int(mtch_dict[st])],
            constants.RE_RANGE_SEST: lambda mtch_dict, dta: dta[int(mtch_dict[s]):int(mtch_dict[e]):int(mtch_dict[st])],
        }
        for key, value in range_map.items():
            match = key.match(range_str)
            if match:
                return value(match.groupdict(), data), search_value
        return [], {}

    def _operator_where(self, data, search_value):
        for sub_dict in self.dict_search(data, search_value):
            yield

    def _select(self, data, search_val):
        if isinstance(search_val, dict):
            for key, val in search_val.items():
                if key in self.array_selectors:
                    yield from self._from_array_selector(key, data, val)
                else:
                    yield from self._select(data.get(key), val)
        elif isinstance(search_val, abc.Hashable):
            if self._iscontainer(data):
                for data_point in data:
                    yield data_point.get(search_val, data)
            else:
                yield data.get(search_val, data)
        else:
            yield data

    def _from_array_selector(self, operator_type, data, search_value):
        if isinstance(search_value, dict):
            try:
                operator, search_value = list(search_value.items())[0]
                yield from self._select(*self._array_operator_map[operator_type](data, search_value, operator))
            except AttributeError:
                yield data
        else:
            yield self._array_operator_map[operator_type](data, {}, search_value)[0]
