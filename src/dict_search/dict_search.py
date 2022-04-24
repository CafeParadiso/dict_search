import re
import types

from . import exceptions


class DictSearch:
    def __init__(self, operator_str=None):
        self._init_precondition(operator_str)
        self.operator_char = operator_str or "$"

        self.lop_ne = f"{self.operator_char}ne"
        self.lop_gt = f"{self.operator_char}gt"
        self.lop_gte = f"{self.operator_char}gte"
        self.lop_lt = f"{self.operator_char}lt"
        self.lop_lte = f"{self.operator_char}lte"
        self.lop_in = f"{self.operator_char}in"
        self.lop_nin = f"{self.operator_char}nin"
        self.lop_regex = f"{self.operator_char}regex"
        self.lop_expr = f"{self.operator_char}expr"
        self.lop_inst = f"{self.operator_char}inst"
        self.low_level_operators = [val for key, val in self.__dict__.items() if re.match(r"^lop_.*$", key)]

        self.hop_and = f"{self.operator_char}and"
        self.hop_or = f"{self.operator_char}or"
        self.hop_xor = f"{self.operator_char}xor"
        self.hop_not = f"{self.operator_char}not"
        self.high_level_operators = [val for key, val in self.__dict__.items() if re.match(r"^hop_.*$", key)]

        self.aop_all = f"{self.operator_char}all"
        self.aop_any = f"{self.operator_char}any"
        self.aop_match = f"{self.operator_char}match"
        self.aop_matchgt = f"{self.operator_char}matchgt"
        self.aop_matchgte = f"{self.operator_char}matchgte"
        self.aop_matchlt = f"{self.operator_char}matchlt"
        self.aop_matchlte = f"{self.operator_char}matchlte"
        self.array_operators = [val for key, val in self.__dict__.items() if re.match(r"^aop_.*$", key)]

        self.sel_index = f"{self.operator_char}index"
        self.sel_range = f"{self.operator_char}range"
        self.array_selectors = [val for key, val in self.__dict__.items() if re.match(r"^sel_.*$", key)]

    @staticmethod
    def _init_precondition(operator_str):
        if operator_str and not isinstance(operator_str, str):
            raise exceptions.OperatorCharError(operator_str)

    def dict_search(self, data, search_dict):
        self._search_precondition(data, search_dict)
        for index, data_point in enumerate(data):
            if not isinstance(data_point, dict):
                continue
            matches = list(self._search(data_point, search_dict))
            if matches and all(matches):
                yield data_point

    @staticmethod
    def _search_precondition(data, search_dict):
        try:
            iter(data)
        except TypeError:
            raise exceptions.PreconditionDataError(data)
        if not isinstance(search_dict, dict):
            raise exceptions.PreconditionSearchDictError(search_dict)

    def _search(self, data, search_dict, matches=None):
        matches = matches if isinstance(matches, list) else []
        if isinstance(search_dict, dict):
            for key, value in search_dict.items():
                if key in self.low_level_operators:
                    for match in self._search(data, key, matches + [self._low_level_operator(key, data, value)]):
                        yield match
                elif key in self.high_level_operators:
                    for match in self._search(
                        data, key, matches + list(self._high_level_operator(key, data, search_dict[key]))
                    ):
                        yield match
                elif key in self.array_operators:
                    # using key as search dict in order to terminate
                    for match in self._search(
                        data,
                        key,
                        matches + list(self._array_operators(key, data, value)),
                    ):
                        yield match
                elif key in self.array_selectors:
                    for match in self._search(*self._array_selector(key, data, value), matches):
                        yield match
                elif all(isinstance(obj, dict) for obj in [value, data]):
                    for match in self._search(data.get(key), value, matches):
                        yield match
                elif isinstance(data, dict):
                    for match in self._search(
                        data.get(key), key, matches + [True if data.get(key) == value else False]
                    ):
                        yield match
                else:
                    yield matches
        else:
            yield from matches

    def _low_level_operator(self, operator, value, search_value):
        operation_map = {
            self.lop_ne: lambda val, search_val: val != search_value,
            self.lop_gt: lambda val, search_val: val > search_val,
            self.lop_gte: lambda val, search_val: val >= search_val,
            self.lop_lt: lambda val, search_val: val < search_val,
            self.lop_lte: lambda val, search_val: val <= search_val,
            self.lop_in: lambda val, search_val: val in search_value,
            self.lop_nin: lambda val, search_val: val not in search_value,
            self.lop_regex: lambda val, search_patt: True if re.compile(search_patt).search(val) else False,
            self.lop_expr: lambda val, func: func(val) if isinstance(func(val), bool) else False,
            self.lop_inst: lambda val, search_type: isinstance(val, search_type),
        }
        try:
            return operation_map[operator](value, search_value)
        except TypeError:  # in case arithmetic comparisons fail
            return False

    def _high_level_operator(self, operator, data, search_iterator):
        if not any(
            [True if isinstance(search_iterator, typ) else False for typ in [list, tuple, set, types.GeneratorType]]
        ):
            raise exceptions.HighLevelOperatorIteratorError
        operator_map = {
            self.hop_and: lambda mtchs: all(mtchs) if mtchs else False,
            self.hop_or: lambda mtchs: any(mtchs),
            self.hop_xor: lambda mtchs: True if mtchs.count(True) == 1 else False,
            self.hop_not: lambda mtchs: False if all(mtchs) or not mtchs else True,
        }
        matches = [match for search_dict in search_iterator for match in self._search(data, search_dict)]
        yield operator_map[operator](matches)

    def _array_operators(self, operator, data, search_value):
        if not any(True if isinstance(data, typ) else False for typ in [list, tuple]):
            return False
        operator_generic_map = {
            self.aop_all: self._operator_all,
            self.aop_any: self._operator_any,
        }
        operator_match_map = {
            self.aop_match: lambda mtchs_c, c: True if mtchs_c == c else False,
            self.aop_matchgt: lambda mtchs_c, c: True if mtchs_c > c else False,
            self.aop_matchgte: lambda mtchs_c, c: True if mtchs_c >= c else False,
            self.aop_matchlt: lambda mtchs_c, c: True if mtchs_c < c else False,
            self.aop_matchlte: lambda mtchs_c, c: True if mtchs_c <= c else False,
        }
        if operator in operator_match_map.keys():
            count, search_value = list(search_value.items())[0]
            try:
                yield operator_match_map[operator](self._match_count(data, search_value), int(count))
            except TypeError:
                return False
        else:
            yield operator_generic_map[operator](data, search_value)

    def _operator_all(self, data, search_value):
        matches = [match for d_point in data for match in self._search(d_point, search_value)]
        return True if matches and all(matches) else False

    def _operator_any(self, data, search_value):
        return any(match for d_point in data for match in self._search(d_point, search_value))

    def _match_count(self, data, search_value):
        if len(search_value.keys()) > 1:  # implicit $and
            search_list = [{key: search_value[key]} for key in search_value]
            matches = [
                    match for d_point in data for match in self._high_level_operator(self.hop_and, d_point, search_list)
                ]
        else:
            matches = [match for d_point in data for match in self._search(d_point, search_value)]
        return matches.count(True)

    def _array_selector(self, operator, data, search_value):
        operator_map = {
            self.sel_index: self._operator_index,
            self.sel_range: self._operator_range,
        }
        try:
            return operator_map[operator](data, search_value)
        except (TypeError, IndexError):
            return [], {}

    @staticmethod
    def _operator_index(data, search_value):
        index, search_value = list(search_value.items())[0]
        return data[int(index)], search_value

    @staticmethod
    def _operator_range(data, search_value):
        range_str, search_value = list(search_value.items())[0]
        s, e, st = "start", "end", "step"
        range_map = {
            re.compile(rf"^(?P<{s}>-?\d+)::?$"): lambda mtch_dict, dta: dta[int(mtch_dict[s]):],  # [s:] | [s::]
            re.compile(rf"^:(?P<{e}>-?\d+):?$"): lambda mtch_dict, dta: dta[:int(mtch_dict[e])],  # [:e] | [:e:]
            re.compile(rf"^::(?P<{st}>-?\d+)$"): lambda mtch_dict, dta: dta[::int(mtch_dict[st])],  # [::st]
            re.compile(rf"^(?P<{s}>-?\d+):(?P<{e}>-?\d+):?$"):
                lambda mtch_dict, dta: dta[int(mtch_dict[s]):int(mtch_dict[e])],  # [s:e] | [s:e:]
            re.compile(rf"^(?P<{s}>-?\d+)::(?P<{st}>-?\d+)$"):
                lambda mtch_dict, dta: dta[int(mtch_dict[s])::int(mtch_dict[st])],  # [s::st]
            re.compile(rf"^:(?P<{e}>-?\d+):(?P<{st}>-?\d+)$"):
                lambda mtch_dict, dta: dta[:int(mtch_dict[e]):int(mtch_dict[st])],  # [:e:st]63
            re.compile(rf"^(?P<{s}>-?\d+):(?P<{e}>-?\d+):(?P<{st}>-?\d+)$"):
                lambda mtch_dict, dta: dta[int(mtch_dict[s]):int(mtch_dict[e]):int(mtch_dict[st])],  # [s:e:st]
        }
        for key, value in range_map.items():
            match = key.match(range_str)
            if match:
                return value(match.groupdict(), data), search_value
        return [], {}
