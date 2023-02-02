import unittest
from datetime import datetime
import re

from src.dict_search import DictSearch
from src.dict_search.utils import find_value
from src.dict_search.operators import exceptions
from src.dict_search import constants
from src.dict_search.operators.operators import low_level_operators as lop

from test.utils import BaseTestOperators, TestCase
from test.new_fixtures import CursedData
from test.new_fixtures.data import COUNTRY_ARGENTINA, COUNTRY_SPAIN, TAX_B, COUNTRY_MORROCCO
from pprint import pprint


class TestEqual(BaseTestOperators.TestOperator):
    op = lop.Equal(1)
    true_args = [1, 1]
    false_args = [2, 3]
    search = DictSearch(match_query={"id": 1})
    func = lambda x: x["id"] == 1


class TestNotEqual(BaseTestOperators.TestOperator):
    op = lop.NotEqual(1)
    true_args = 2
    false_args = 1
    search = DictSearch(match_query={"id": {"$ne": 1}})
    func = lambda x: x["id"] != 1


class TestGreater(BaseTestOperators.TestOperator):
    value = datetime(2022, 5, 1)
    op = lop.Greater(1)
    true_args = 2
    false_args = [1, 0]
    search = DictSearch(match_query={"info": {"departure": {"$gt": value}}})
    func = lambda x: x["info"]["departure"] > TestGreater.value


class TestGreaterEq(BaseTestOperators.TestOperator):
    value = datetime(2022, 6, 1)
    op = lop.GreaterEq(1)
    true_args = [2, 1]
    false_args = 0
    search = DictSearch(match_query={"info": {"departure": {"$gte": value}}})
    func = lambda x: x["info"]["departure"] >= TestGreaterEq.value


class TestLessThen(BaseTestOperators.TestOperator):
    value = datetime(2022, 6, 1)
    op = lop.LessThen(1)
    true_args = 0
    false_args = [1, 2]
    search = DictSearch(match_query={"info": {"departure": {"$lt": value}}})
    func = lambda x: x["info"]["departure"] < TestLessThen.value


class TestLessThenEq(BaseTestOperators.TestOperator):
    value = datetime(2022, 6, 1)
    op = lop.LessThenEq(1)
    true_args = [0, 1]
    false_args = 2
    search = DictSearch(match_query={"info": {"departure": {"$lte": value}}})
    func = lambda x: x["info"]["departure"] <= TestLessThenEq.value


class TestIs(BaseTestOperators.TestOperator):
    op = lop.Is(True)
    true_args = True
    false_args = False
    search = DictSearch(match_query={"in_route": {"$is": True}})
    func = lambda x: x["in_route"] is True


class TestIn(BaseTestOperators.TestOperator):
    values = [COUNTRY_ARGENTINA, COUNTRY_SPAIN]
    op = lop.In([1])
    true_args = 1
    false_args = 2
    search = DictSearch(match_query={"info": {"origin": {"$in": values}}})
    func = lambda x: x["info"]["origin"] in TestIn.values


class TestNotIn(BaseTestOperators.TestOperator):
    values = [COUNTRY_ARGENTINA, COUNTRY_SPAIN]
    op = lop.NotIn([1])
    true_args = 2
    false_args = 1
    search = DictSearch(match_query={"info": {"origin": {"$nin": values}}})
    func = lambda x: x["info"]["origin"] not in TestNotIn.values


class TestContains(BaseTestOperators.TestOperator):
    value = TAX_B
    op = lop.Contains(1)
    true_args = {1}
    false_args = {2}
    search = DictSearch(match_query={"taxes": {"$cont": value}})
    func = lambda x: TestContains.value in x["taxes"]


class TestNotContains(BaseTestOperators.TestOperator):
    value = TAX_B
    op = lop.NotContains(1)
    true_args = {2}
    false_args = {1}
    search = DictSearch(match_query={"taxes": {"$ncont": value}})
    func = lambda x: TestNotContains.value not in x["taxes"]


class TestRegex(BaseTestOperators.TestOperator, BaseTestOperators.ExceptionsMixin):
    pattern_str = "^m[ie]+aw"
    value = re.compile(".*01.*", re.IGNORECASE)
    op = lop.Regex(pattern_str)
    true_args = ["miaw", "mieaw", "mieeeaw", "mieeeaw"]
    false_args = ["miw", "mmieaw", "maw"]
    search = DictSearch(match_query={"info": {"port_code": {"$regex": value}}})
    func = lambda x: TestRegex.value.search(x["info"]["port_code"])
    exceptions = lambda: lop.Regex(12), exceptions.RegexOperatorException

    def test_regex_pattern(self):
        self.op = lop.Regex(re.compile("^m[ie]+aw"))
        super(TestRegex, self).test_implementation()


class TestFunction(BaseTestOperators.TestOperator):
    value = lambda x: sum(x) >= 0.5
    op = lop.Function(value)
    true_args = [[0.1, 0.2, 0.2], [0.3, 0.2]]
    false_args = [[0.2, 0.2]]
    search = DictSearch(match_query={"taxes": {"$func": value}})
    func = lambda x: TestFunction.value(x["taxes"])


class TestIsInstance(BaseTestOperators.TestOperator):
    value = list
    op = lop.IsInstance(value)
    true_args = [[]]
    false_args = [{}, 123, "abc", value]
    search = DictSearch(match_query={"port_route": {"$inst": value}})
    func = lambda x: isinstance(x["port_route"], TestIsInstance.value)


class TestCompare(BaseTestOperators.TestOperator, BaseTestOperators.ExceptionsMixin):
    value = 2
    t_keys = ["info", "ship_country"]
    t_func = lambda x, y: y == x
    fixture = {"info": {"ship_country": 2}}
    op = lop.Compare(t_keys, func=t_func)
    op.keys = t_keys
    op.func = t_func
    true_args = value, fixture
    false_args = 3, fixture
    search = DictSearch(match_query={"info": {"origin": {"$comp": [t_keys, t_func]}}})
    func = lambda x: x["info"].get("ship_country") == x["info"]["origin"]
    exceptions = [
        (lambda: lop.Compare({}), exceptions.CompOperatorFirstArgError),
        (lambda: lop.Compare([1, {}]), exceptions.CompOperatorFirstArgError),
        (lambda: lop.Compare(1, func=2), exceptions.CompOperatorSecondArgError),
        (lambda: DictSearch(match_query={"$comp": 2}), exceptions.CompOperatorTypeError),
    ]


class TestFind(BaseTestOperators.TestOperator, BaseTestOperators.ExceptionsMixin):
    value = COUNTRY_MORROCCO
    fixture_data = {"a": {"b": {"c": 12}}, "d": {"e": 34}}
    search = DictSearch(match_query={"$find": ["ship_country", value]})
    exceptions = [
        (lambda: lop.Find({1: 2}), Exception),
        (lambda: lop.Find([CursedData()]), Exception),
        (lambda: DictSearch(match_query={"$find": 2}), Exception),
        (lambda: DictSearch(match_query={"$find": [2]}), Exception),
    ]

    def setUp(self) -> None:
        self.func = self.check
        super(TestFind, self).setUp()

    def check(self, x):
        result = find_value(x, "ship_country")
        if isinstance(result, list):
            result = [r.result for r in result]
        else:
            result = result.result
        return self.value == result

    def test_implementation(self):
        for attr, op in [
            [(self.fixture_data, lambda x: x == 34), lop.Find("e")],
            [(self.fixture_data, lambda x: x == 12), lop.Find("c")],
            [(self.fixture_data, lambda x: not x.found), lop.Find("z")],
        ]:
            attr = [attr] if not isinstance(attr, list) else attr
            for args in attr:
                self.assertTrue(args[1](op(args[0])), f"{op.keys}")
