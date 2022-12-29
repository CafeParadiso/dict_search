from collections.abc import Iterator

from .. import exceptions
from ..bases import ArraySelector
from ..constants import SLICING_PATTERN


class Where(ArraySelector):
    name = "where"

    def __init__(self, search_val, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_val = search_val

    def implementation(self, data, search_instance):
        if isinstance(data, Iterator):
            raise exceptions.WhereIteratorException(self.name, data)
        prev_match_query = search_instance.match_query
        try:
            search_instance.match_query = self.search_val
            matched_data = list(filter(lambda x: x is not None, map(lambda x: search_instance(x), data)))
        finally:
            search_instance.match_query = prev_match_query
        return matched_data


class Index(ArraySelector):
    name = "index"

    def __init__(self, index, **kwargs):
        super().__init__(**kwargs)
        self.index = self.precondition(index)

    def implementation(self, data):
        if not isinstance(self.index, list):
            try:
                return data[self.index]
            except IndexError:
                return self.default_return
        values = []
        for i in self.index:
            try:
                values.append(data[i])
            except IndexError:
                continue
        if not values:
            return self.default_return
        return values

    def precondition(self, index):
        if not isinstance(index, (int, list)):
            raise Exception
        if isinstance(index, list) and not all(isinstance(x, int) for x in index):
            raise Exception
        return index


class Slice(ArraySelector):
    name = "slice"

    def __init__(self, slice_str, **kwargs):
        super().__init__(**kwargs)
        self.slice_str = self.precondition(slice_str)

    def implementation(self, data):
        return eval(f"data[{self.slice_str}]", {"data": data})

    def precondition(self, slice_str):
        if not isinstance(slice_str, str) or not SLICING_PATTERN.match(slice_str):
            raise exceptions.SliceSelectionOperatorError(slice_str)
        return slice_str
