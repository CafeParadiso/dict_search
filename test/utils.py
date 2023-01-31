import unittest
from .new_fixtures import read_fixtures
from src.dict_search import DictSearch, Operator
from test.new_fixtures.data import get_data
from pprint import pprint


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
                count = count + 1 if search(d_point) else count
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


class BaseTestOperators:
    """The outer class serves as a patch to avoid test discovery of the base class since it would fail"""

    class TestOperator(unittest.TestCase):
        op = None
        data = None
        search = None
        func = None
        precondition = None
        true_args = None
        false_args = None

        def setUp(self) -> None:
            self.data = get_data()

        def test_search(self):
            results, other_results = [], []
            for d_point in self.data:
                if self.search(d_point):
                    results.append(d_point)
                else:
                    other_results.append(d_point)
            func = self.__class__.func or self.func
            self.assertTrue(results, msg=f"No results were found for query:\n{self.search.match_query}")
            self.assertTrue(
                all(func(v) for v in results),
                msg=f"All found values do not match the assertion function, check the query:\n{self.search.match_query}"
            )
            self.assertFalse(
                any(func(v) for v in other_results),
                msg=f"Some discarded results match the assertion function, check the query:\n{self.search.match_query}"
            )

        def test_implementation(self):
            assert all(x is not None for x in [self.true_args, self.false_args])
            for attr, assertion in [(self.true_args, self.assertTrue), (self.false_args, self.assertFalse)]:
                attr = [attr] if not isinstance(attr, list) else attr
                for arguments in attr:
                    arguments = (arguments,) if not isinstance(arguments, tuple) else arguments
                    assertion(self.op.implementation(*arguments))

        def filter_results(self, search=None):
            search = self.search if not search else search
            return list(filter(lambda x: x is not None, map(lambda x: search(x), self.data)))

    class TestOperatorMultipleSearch(TestOperator):
        def test_search(self):
            search_list = self.search
            for search_inst, func in search_list:
                self.__class__.func = func
                self.search = search_inst
                super().test_search()

    class ExceptionsMixin(unittest.TestCase):
        exceptions = None

        def test_exceptions(self):
            self.exceptions = [self.exceptions] if not isinstance(self.exceptions, list) else self.exceptions
            for func, exc in self.exceptions:
                with self.assertRaises(exc):
                    func()


class DemoOpModulo(Operator):
    name = "modulo"
    default_return = False

    def __init__(self, denominator, reminder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.denominator = denominator
        self.reminder = reminder

    def implementation(self, data):
        return data % self.denominator == self.reminder

    @classmethod
    def init_match_node(cls, match_query, parse_func):
        pass
