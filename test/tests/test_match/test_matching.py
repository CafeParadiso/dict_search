from pprint import pprint
from urllib import parse

from src.dict_search import DictSearch
from src.dict_search import HighLevelOperator, MatchOperator
from src.dict_search import Operator
from src.dict_search import exceptions
from src.dict_search.operators.operators import low_level_operators as lop
from unittest import TestCase
from test.new_fixtures import CursedData
from test.utils import DemoOpModulo


class TestDictSearch(TestCase):
    @staticmethod
    def get_consumable_fixture():
        return [
            {"a": (1 for _ in range(3)), "id": 0},
            {"a": map(lambda x: 2 * x, (2 for _ in range(3))), "id": 1},
            {"a": [1 for _ in range(3)], "id": 2}
        ]

    def test_operator_char(self):
        operator_str = "!"
        data = [{"$len": 1}, {"$len": 3}, {"$len": 2}]
        search = DictSearch(match_query={"$len": {f"{operator_str}gt": 2}}, ops_str=operator_str)
        assert f"{operator_str}gt" in search.all_match_ops
        values = search.filter(data)
        assert list(values) == [data[1]]

    def test_consumable_iterators(self):
        from collections.abc import Iterator
        search = DictSearch(match_query={"a": {"$all": 1}})
        results = list(search.filter(self.get_consumable_fixture()))
        assert results and isinstance(results[0]["a"], Iterator)
        search.consumable_iterators = Iterator
        results = list(search.filter(self.get_consumable_fixture()))
        assert results and isinstance(results[0]["a"], list)

    def test_non_consumable_iterators(self):
        from collections.abc import Iterator
        search = DictSearch(match_query={"a": {"$all": 1}}, consumable_iterators=Iterator, non_consumable_iterators=map)
        data = self.get_consumable_fixture()
        results = list(search.filter(data))
        assert results and isinstance(results[0]["a"], list) and isinstance(data[1]["a"], map)

    def test_consumable_cast_type(self):
        from collections.abc import Iterator
        search = DictSearch(match_query={"a": {"$all": 1}}, consumable_iterators=Iterator, consumable_cast_type=tuple)
        results = list(search.filter(self.get_consumable_fixture()))
        assert results and isinstance(results[0]["a"], tuple)


class TestMatchExceptions(TestCase):
    def test_ops_config_error(self):
        ops_config = {"eq": {"fail": 1}}
        with self.assertRaises(exceptions.OpsConfigKeyError):
            DictSearch(ops_init_config=ops_config)

    def test_load_ops_error(self):
        search = DictSearch()
        with self.assertRaises(exceptions.LoadOpsError):
            search._load_ops_from_module(lop)

    def test_custom_ops_value_error(self):
        with self.assertRaises(exceptions.CustomOpsValueError):
            DictSearch(ops_custom="a")

    def test_custom_ops_existing_key_error(self):
        class BrokenOp(Operator):
            name = "eq"
            default_return = False

            def implementation(self, *args):
                pass

        with self.assertRaises(exceptions.CustomOpsExistingKey):
            DictSearch(ops_custom=BrokenOp)


class TestMatching(TestCase):
    simple_fixture = [
        {"a": 0, "b": {"c": 2}},
        {"a": 1, "b": {"c": 1}},
        {"a": 2, "b": {"c": 2}},
        {"a": 1},
    ]

    def test_str_name(self):
        comp = "<class 'test.utils.DemoOpModulo'> modulo\ndefault_return: False\nallowed_types: None\nignored_types: " \
               "None\nexpected_exc: None\n"
        self.assertEqual(str(DemoOpModulo(1, 1)), comp)

    def test_ops_config(self):
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
        search = DictSearch({"$match": {1: [{"$ne": 1, "$and": [{}]}]}}, ops_init_config=ops_config)
        assert search.inner_eq_op.allowed_types == object
        assert search.get_operator("match").allowed_types == int
        assert search.get_operator("match").ignored_types == list
        assert search.get_operator("match").default_return is False
        assert search.get_operator("match").expected_exc == {ReferenceError: True}
        assert search.get_operator("and").allowed_types == int
        assert search.get_operator("and").ignored_types == (int, str)
        assert search.get_operator("and").default_return is True
        assert search.get_operator("and").expected_exc == {ValueError: False, IndexError: True, PermissionError: False}
        assert search.get_operator("ne").allowed_types == object
        assert search.get_operator("ne").ignored_types is None
        assert search.get_operator("ne").default_return is False
        assert search.get_operator("ne").expected_exc == {Exception: False, BrokenPipeError: False}

    def test_simple_field(self):
        results = list(DictSearch(match_query={"a": 1}).filter(self.simple_fixture))
        assert results and all(x["a"] == 1 for x in results)

    def test_nested_field(self):
        results = list(DictSearch(match_query={"b": {"c": 2}}).filter(self.simple_fixture))
        assert results and all(x["b"]["c"] == 2 for x in results)

    def test_multiple_fields(self):
        results = list(DictSearch(match_query={"b": {"c": 2}, "a": 0}).filter(self.simple_fixture))
        assert results and all(x["b"]["c"] == 2 and x["a"] == 0 for x in results)

    def test_mixed_type_data(self):
        data = [{"len": 2}, "2333", {"len": 2}]
        results = list(DictSearch({"len": 2}).filter(data))
        assert results == [data[0], data[-1]]

    def test_search_dict_precondition(self):
        with self.assertRaises(exceptions.PreconditionError):
            DictSearch(match_query="23")

    def test_custom_op(self):
        data = [{"a": 3}, {"a": 2}, {"a": 5}, {"a": 6}]
        search = DictSearch(match_query={"a": {"$modulo": [2, 0]}}, ops_custom=DemoOpModulo)
        results = list(search.filter(data))
        self.assertEqual(results, [data[1], data[3]])
        print(results)

    def test_get_operator(self):
        func = lambda x, y: x * 2 == y
        search = DictSearch(
            match_query={"a": {"$or": [{"$comp": [["a", "b"]]}, {"$comp": [["a", "b"], func]}]}}
        )
        self.assertTrue(search.get_operator("or"))
        self.assertNotEqual(search.get_operator("comp", {"func": func}), search.get_operator("comp"))
