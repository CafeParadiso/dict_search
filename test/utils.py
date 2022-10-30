import unittest
from .new_fixtures import read_fixtures
from src.dict_search import DictSearch, Operator


class TestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.data = list(read_fixtures())

    def matching_test(self, match_query, **kwargs):
        search = DictSearch(match_query=match_query, **kwargs)
        values = list(filter(lambda x: x is not None, map(lambda x: search(x), self.data)))
        ids = [v["id"] for v in values]
        other_values = [v for v in self.data if v["id"] not in ids]
        assert len(values) + len(other_values) == len(self.data)
        assert isinstance(values, list) and values
        return values, other_values

    def hop_matching_test(self, match_query, func):
        values = self.matching_test(match_query=match_query)[0]
        search = DictSearch()
        assertion_values = []
        for d_point in self.data:
            count = 0
            for query in list(match_query[list(match_query.keys())[0]].values())[0]:
                search.match_query = query
                count = count + 1 if all(search._apply_match(d_point, search.match_query)) else count
            if func(count):
                assertion_values.append(d_point)
        assert values == assertion_values

    def selection_test(self, select_query, **kwargs):
        search = DictSearch(select_query=select_query, **kwargs)
        for index, dp in enumerate(self.data):
            sel = search(dp)
            assert dp.keys() == list(read_fixtures())[index].keys()
            yield sel, dp

    @staticmethod
    def get_search(**kwargs):
        return DictSearch(**kwargs)

    @staticmethod
    def filter_results(search, data):
        return list(filter(lambda x: x is not None, map(lambda x: search(x), data)))


class TestOpModulo(Operator):
    name = "modulo"
    initial_default_return = False

    def implementation(self, data, denominator, reminder):
        return data % denominator == reminder
