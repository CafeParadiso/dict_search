import unittest
from datetime import datetime
import re

from src.dict_search import DictSearch
from src.dict_search.utils import find_value
from src.dict_search.operators import exceptions
from src.dict_search import constants
from src.dict_search.operators.operators import low_level_operators as lop

from test.utils import BaseTestLowLevelOperators, BaseTestPrecondition, TestCase
from test.new_fixtures.data import COUNTRY_ARGENTINA, COUNTRY_SPAIN, TAX_B, COUNTRY_MORROCCO
from pprint import pprint


class TestEqual(BaseTestLowLevelOperators.CaseLowLevelOperators):
    op = lop.Equal()
    true_args = 1, 1
    false_args = 2, 1
    search = DictSearch(match_query={"id": 1})
    func = lambda x: x["id"] == 1


class TestNotEqual(BaseTestLowLevelOperators.CaseLowLevelOperators):
    op = lop.NotEqual()
    true_args = 1, 2
    false_args = 1, 1
    search = DictSearch(match_query={"id": {"$ne": 1}})
    func = lambda x: x["id"] != 1


class TestGreater(BaseTestLowLevelOperators.CaseLowLevelOperators):
    value = datetime(2022, 6, 1)
    op = lop.Greater()
    true_args = 2, 1
    false_args = [(1, 1), (0, 1)]
    search = DictSearch(match_query={"info": {"arrival": {"$gt": value}}})
    func = lambda x: x["info"]["arrival"] > TestGreater.value


class TestGreaterEq(BaseTestLowLevelOperators.CaseLowLevelOperators):
    value = datetime(2022, 6, 1)
    op = lop.GreaterEq()
    true_args = [(2, 1), (1, 1)]
    false_args = 0, 1
    search = DictSearch(match_query={"info": {"arrival": {"$gte": value}}})
    func = lambda x: x["info"]["arrival"] >= TestGreaterEq.value


class TestLessThen(BaseTestLowLevelOperators.CaseLowLevelOperators):
    value = datetime(2022, 6, 1)
    op = lop.LessThen()
    true_args = 0, 1
    false_args = [(1, 1), (2, 1)]
    search = DictSearch(match_query={"info": {"arrival": {"$lt": value}}})
    func = lambda x: x["info"]["arrival"] < TestLessThen.value


class TestLessThenEq(BaseTestLowLevelOperators.CaseLowLevelOperators):
    value = datetime(2022, 6, 1)
    op = lop.LessThenEq()
    true_args = [(0, 1), (1, 1)]
    false_args = 2, 1
    search = DictSearch(match_query={"info": {"arrival": {"$lte": value}}})
    func = lambda x: x["info"]["arrival"] <= TestLessThenEq.value


class TestIs(BaseTestLowLevelOperators.CaseLowLevelOperators):
    op = lop.Is()
    true_args = True, True
    false_args = True, False
    search = DictSearch(match_query={"in_route": {"$is": True}})
    func = lambda x: x["in_route"] is True


class TestIn(BaseTestLowLevelOperators.CaseLowLevelOperators):
    values = [COUNTRY_ARGENTINA, COUNTRY_SPAIN]
    op = lop.In()
    true_args = 1, [1]
    false_args = 2, [1]
    search = DictSearch(match_query={"info": {"origin": {"$in": values}}})
    func = lambda x: x["info"]["origin"] in TestIn.values


class TestNotIn(BaseTestLowLevelOperators.CaseLowLevelOperators):
    values = [COUNTRY_ARGENTINA, COUNTRY_SPAIN]
    op = lop.NotIn()
    true_args = 2, [1]
    false_args = 1, [1]
    search = DictSearch(match_query={"info": {"origin": {"$nin": values}}})
    func = lambda x: x["info"]["origin"] not in TestNotIn.values


class TestContains(BaseTestLowLevelOperators.CaseLowLevelOperators):
    value = TAX_B
    op = lop.Contains()
    true_args = [1], 1
    false_args = [2], 1
    search = DictSearch(match_query={"taxes": {"$cont": value}})
    func = lambda x: TestContains.value in x["taxes"]


class TestNotContains(BaseTestLowLevelOperators.CaseLowLevelOperators):
    value = TAX_B
    op = lop.NotContains()
    true_args = [2], 1
    false_args = [1], 1
    search = DictSearch(match_query={"taxes": {"$ncont": value}})
    func = lambda x: TestNotContains.value not in x["taxes"]


class TestRegex(BaseTestLowLevelOperators.CaseLowLevelOperators, BaseTestPrecondition.CaseTestPrecondition):
    pattern_str = "m[ie]+aw"
    pattern_re = re.compile("m[ie]+aw")
    value = re.compile("ye*s?", re.IGNORECASE)
    op = lop.Regex()
    true_args = [("miaw", pattern_str), ("mieaw", pattern_str), ("mieeeaw", pattern_re), ("mieeeaw", pattern_re)]
    false_args = [(pattern_str, "miw"), (pattern_str, "mmieaw"), (pattern_str, "maw")]
    search = DictSearch(match_query={"info": {"paid": {"$regex": value}}})
    func = lambda x: TestRegex.value.search(x["info"]["paid"])
    precondition = 12, exceptions.RegexOperatorException


class TestFunction(BaseTestLowLevelOperators.CaseLowLevelOperators):
    value = lambda x: sum(x) == 0.5 if isinstance(x, list) else False
    op = lop.Function()
    true_args = [([0.1, 0.2, 0.2], value), ([0.3, 0.2], value)]
    false_args = [([0.2, 0.2], value), ([0.3, 0.3], value)]
    search = DictSearch(match_query={"taxes": {"$func": value}})
    func = lambda x: TestFunction.value(x["taxes"]) if "taxes" in x and isinstance(x["taxes"], list) else False


class TestIsInstance(BaseTestLowLevelOperators.CaseLowLevelOperators):
    value = list
    op = lop.IsInstance()
    true_args = [], value
    false_args = [({}, value), (123, value), ("abc", value)]
    search = DictSearch(match_query={"ports": {"$inst": value}})
    func = lambda x: isinstance(x["ports"], TestIsInstance.value)


class TestCompare(BaseTestLowLevelOperators.CaseLowLevelOperators, BaseTestPrecondition.CaseTestPrecondition):
    value = 2
    t_keys = ["info", "origin"]
    t_func = lambda x, y: y == x
    fixture = {"info": {"origin": 2}}
    op = lop.Compare()
    op.keys = t_keys
    op.func = t_func
    true_args = value, fixture
    false_args = 3, fixture
    search = DictSearch(match_query={"info": {"ship_country": {"$comp": [t_keys, t_func]}}})
    func = lambda x: x["info"]["origin"] == x["info"]["ship_country"]
    precondition = [
        ((1, 2), exceptions.CompOperatorTypeError),
        ([1, 2, 3], exceptions.CompOperatorTypeError),
        ([set([1]), 2], exceptions.CompOperatorFirstArgError),
        ([[1, set([1])], 2], exceptions.CompOperatorFirstArgError),
        ([1, 2], exceptions.CompOperatorSecondArgError),
    ]


class TestFind(BaseTestLowLevelOperators.CaseLowLevelOperators):
    value = COUNTRY_MORROCCO
    fixture_data = {"a": {"b": {"c": 12}}, "d": {"e": 34}}
    op = lop.Find()
    true_args = [(fixture_data, "e", lambda x: x == 34), (fixture_data, ["b", "c"], lambda x: x == 12)]
    false_args = 3, fixture_data, lambda x: not x
    search = DictSearch(match_query={"$find": ["ship_country", value]})
    func = lambda x: [TestFind.value] == find_value(x, "ship_country")

    def test_implementation(self):
        for attr in [self.true_args, self.false_args]:
            attr = [attr] if not isinstance(attr, list) else attr
            for args in attr:
                args[-1](self.op.implementation(*args[:-1]))
