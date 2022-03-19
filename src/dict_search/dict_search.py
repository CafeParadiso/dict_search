import logging
import re
import types

from . import exceptions


class DictSearch:
    def __init__(self, operator_str=None, **kwargs):
        self._init_precondition(operator_str)
        self.operator_char = operator_str or "$"
        self.lop_ne = f"{self.operator_char}ne"
        self.lop_lt = f"{self.operator_char}lt"
        self.lop_lte = f"{self.operator_char}lte"
        self.lop_gt = f"{self.operator_char}gt"
        self.lop_gte = f"{self.operator_char}gte"
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
        self.array_operators = [val for key, val in self.__dict__.items() if re.match(r"^aop_.*$", key)]

        self.sel_index = f"{self.operator_char}index"
        self.sel_last = f"{self.operator_char}last"
        self.array_selectors = [val for key, val in self.__dict__.items() if re.match(r"^sel_.*$", key)]

        self._init_logger(**kwargs)

    @staticmethod
    def _init_precondition(operator_str):
        if operator_str and not isinstance(operator_str, str):
            raise exceptions.OperatorCharError(operator_str)

    @staticmethod
    def _init_logger(**kwargs):
        logging.basicConfig(**kwargs)

    def dict_search(self, data, search_dict):
        self._search_precondition(data, search_dict)
        for index, data_point in enumerate(data):
            if not isinstance(data_point, dict):
                continue
            logging.info(f"Document: {index + 1}")
            matches = list(self._search(data_point, search_dict))
            if all(matches):
                logging.info(f"Document: {index + 1} matched")
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
                logging.debug(f"{key}")
                if key in self.low_level_operators:
                    for match in self._search(data, key, matches + [self._low_level_operator(key, data, value)]):
                        logging.debug(f"{data} {key} {value}: {match}")
                        yield match
                elif key in self.high_level_operators:
                    for match in self._search(
                        data, key, matches + list(self._high_level_operator(key, data, search_dict[key]))
                    ):
                        logging.debug(f"{key}: {match}")
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
                elif isinstance(value, dict):
                    for match in self._search(data.get(key), value, matches):
                        yield match
                elif isinstance(data, dict):
                    for match in self._search(
                        data.get(key), key, matches + [True if data.get(key) == value else False]
                    ):
                        logging.debug(f"{data.get(key)} == {value}: {match}")
                        yield match
                else:
                    yield matches
        else:
            yield from matches

    def _low_level_operator(self, operator, value, search_value):
        operation_map = {
            self.lop_ne: lambda val, search_val: val != search_value,
            self.lop_lt: lambda val, search_val: val < search_val,
            self.lop_lte: lambda val, search_val: val <= search_val,
            self.lop_gt: lambda val, search_val: val > search_val,
            self.lop_gte: lambda val, search_val: val >= search_val,
            self.lop_in: lambda val, search_val: val in search_value,
            self.lop_nin: lambda val, search_val: val not in search_value,
            self.lop_regex: lambda val, search_patt: True if re.compile(search_patt).search(val) else False,
            self.lop_inst: lambda val, search_type: isinstance(val, search_type),
        }
        if operator == self.lop_expr:  # the search key 'expr' must be treated differently
            value = search_value[0](value)
            if isinstance(search_value[1], dict):
                operator, search_value = list(search_value[1].items())[0]
            else:
                return True if value == search_value[1] else False
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
        operator_map = {
            self.aop_all: self._operator_all,
            self.aop_any: self._operator_any,
            self.aop_match: self._operator_match,
        }
        yield operator_map[operator](data, search_value)

    def _operator_all(self, data, search_value):
        if not any(True if isinstance(data, typ) else False for typ in [list, tuple]):
            return False
        matches = [match for d_point in data for match in self._search(d_point, search_value)]
        return True if matches and all(matches) else False

    def _operator_any(self, data, search_value):
        matches = [match for d_point in data for match in self._search(d_point, search_value)]
        return any(matches)

    def _operator_match(self, data, search_value):
        count, search_value = list(search_value.items())[0]
        try:
            count = int(count)
        except TypeError:
            return False
        if len(search_value.keys()) > 1:  # implicit $and
            search_list = [{key: search_value[key]} for key in search_value]
            matches = [
                match
                for match in [
                    match
                    for d_point in data
                    for match in self._high_level_operator(self.hop_and, d_point, search_list)
                ]
            ]
        else:
            matches = [match for d_point in data for match in self._search(d_point, search_value)]
        return True if matches.count(True) >= count else False

    def _array_selector(self, operator, data, search_value):
        operator_map = {
            self.sel_index: self._operator_index,
            self.sel_last: self._operator_last,
        }
        return operator_map[operator](data, search_value)

    @staticmethod
    def _operator_index(data, search_value):
        index, search_value = list(search_value.items())[0]
        index = int(index)
        try:
            return data[index], search_value
        except (TypeError, IndexError):
            return [], {}

    @staticmethod
    def _operator_last(data, search_value):
        try:
            return data[-1], search_value
        except (TypeError, IndexError):
            return [], {}
