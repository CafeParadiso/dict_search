from pprint import pprint

from src.dict_search import DictSearch
from src.dict_search import HighLevelOperator, MatchOperator
from src.dict_search import Operator
from src.dict_search import exceptions
from test.utils import TestCase
from test.new_fixtures import CursedData


class TestMatching(TestCase):
    def test_simple_field(self):
        q = 3
        values, other_values = self.matching_test({"id": q})
        for v in values:
            assert v["id"] == q
        for v in other_values:
            assert v["id"] != q

    def test_nested_field(self):
        q = "Italy"
        values, other_values = self.matching_test({"info": {"origin": "Italy"}})
        for v in values:
            assert v["info"]["origin"] == q
        for v in other_values:
            assert v["info"]["origin"] != q

    def test_multiple_fields(self):
        q = "Peru"
        values, other_values = self.matching_test({"info": {"origin": "Peru"}, "reviewed": False})
        for v in values:
            assert v["info"]["origin"] == q and v["reviewed"] is False
        for v in other_values:
            assert not (v["info"]["origin"] == q and v["reviewed"] is False)

    def test_search_dict_precondition(self):
        with self.assertRaises(exceptions.PreconditionError):
            DictSearch([{"a": 1}])

    def test_mixed_type_data(self):
        data = [{"len": 2}, "2333", {"len": 2}]
        search = DictSearch({"len": 2})
        values = list(filter(lambda x: x is not None, map(lambda x: search(x), data)))
        assert values == [data[0], data[-1]]

    def test_operator_char(self):
        operator_str = "!"
        data = [{"$len": 1}, {"$len": 3}, {"$len": 2}]
        search = DictSearch({"$len": {f"{operator_str}gt": 2}}, ops_str=operator_str)
        values = list(filter(lambda x: x is not None, map(lambda x: search(x), data)))
        assert values == [data[1]]

    def test_unexpected_exception(self):
        data = [{"a": 2}, {"a": CursedData()}]
        with self.assertRaises(Exception):
            search = DictSearch(({"a": 2}))
            list(filter(lambda x: x is not None, map(lambda x: search(x), data)))

    def test_expected_exception(self):
        data = [{"a": 2}, {"a": CursedData(OverflowError)}]
        with self.assertRaises(Exception):
            search = DictSearch(({"a": 2}))
            list(filter(lambda x: x is not None, map(lambda x: search(x), data)))

    def test_ops_config(self):
        data = [{"a": 2}, {"a": CursedData()}]
        ops_config = {
            "ne": {
                "expected_exc": (Exception, BrokenPipeError),
                "default_return": False,
            },
            Operator: {"allowed_types": object},
            MatchOperator: {"ignored_types": list},
            HighLevelOperator: {
                "expected_exc": {ValueError: False, IndexError: True, PermissionError: False},
                "default_return": True,
                "allowed_types": int,
                "ignored_types": (int, str),
            },
            "match": {
                "expected_exc": ReferenceError,
                "default_return": False,
            },
        }
        search = DictSearch({"$match": {1: [{"a": 1}]}}, ops_init_config=ops_config)
        results = self.filter_results(search, data)
