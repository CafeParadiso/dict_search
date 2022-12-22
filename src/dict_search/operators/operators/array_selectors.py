from collections.abc import Iterator

from .. import exceptions
from ..bases import ArraySelector
from ..constants import SLICING_PATTERN, CONTAINER_TYPE


class Where(ArraySelector):
    name = "where"

    def implementation(self, data, search_value, search_instance):
        if isinstance(data, Iterator):
            raise exceptions.WhereIteratorException(self.name, data)
        prev_match_query = search_instance.match_query
        try:
            search_instance.match_query = search_value
            matched_data = list(filter(lambda x: x is not None, map(lambda x: search_instance(x), data)))
        finally:
            search_instance.match_query = prev_match_query
        return matched_data

    def precondition(self, value):
        if not isinstance(value, CONTAINER_TYPE) or len(value) != 2:
            raise exceptions.WhereOperatorError


class Index(ArraySelector):
    name = "index"

    def implementation(self, data, index):
        if not isinstance(index, list):
            try:
                return data[index]
            except IndexError:
                return self.default_return
        values = []
        for i in index:
            try:
                values.append(data[i])
            except IndexError:
                continue
        if not values:
            return self.default_return
        return values


class Slice(ArraySelector):
    name = "slice"

    def implementation(self, data, slice_str):
        return eval(f"data[{slice_str}]", {"data": data})

    def precondition(self, value):
        super().precondition(value)
        if len(value) != 2:
            raise exceptions.SliceSelectionOperatorError(value)
        slice_str = value[0]
        if not isinstance(slice_str, str) or not SLICING_PATTERN.match(slice_str):
            raise exceptions.SliceSelectionOperatorError(slice_str)
