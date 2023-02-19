from datetime import datetime
import re

from src.dict_search import DictSearch
from src.dict_search.utils import find_value
from src.dict_search.operators import exceptions
from src.dict_search.operators.operators import low_level_operators as lop

from test.utils import BaseTestOperators as Base
from test.new_fixtures import CursedData
from test.new_fixtures.data import COUNTRY_ARGENTINA, COUNTRY_SPAIN, TAX_B, COUNTRY_MORROCCO


class TestEqual(Base.OperatorMixin, Base.SearchMixin):
    operator_checks = lop.Equal(1), [1, 1], [2, 3]
    search_checks = DictSearch(match_query={"id": 1}), lambda x: x["id"] == 1


class TestNotEqualTestEqual(Base.OperatorMixin, Base.SearchMixin):
    operator_checks = lop.NotEqual(1), 2, 1
    search_checks = DictSearch(match_query={"id": {"$ne": 1}}), lambda x: x["id"] != 1


class TestGreater(Base.OperatorMixin, Base.SearchMixin):
    value = datetime(2022, 5, 1)
    operator_checks = lop.Greater(1), 2, [1, 0]
    search_checks = \
        DictSearch(match_query={"info": {"departure": {"$gt": value}}}), \
        lambda x: x["info"]["departure"] > TestGreater.value


class TestGreaterEq(Base.OperatorMixin, Base.SearchMixin):
    value = datetime(2022, 6, 1)
    operator_checks = lop.GreaterEq(1), [2, 1], 0
    search_checks = DictSearch(match_query={"info": {"departure": {"$gte": value}}}), lambda x: x["info"]["departure"] >= TestGreaterEq.value


class TestLessThen(Base.OperatorMixin, Base.SearchMixin):
    value = datetime(2022, 6, 1)
    operator_checks = lop.LessThen(1), 0, [1, 2]
    search_checks = DictSearch(match_query={"info": {"departure": {"$lt": value}}}), lambda x: x["info"]["departure"] < TestLessThen.value


class TestLessThenEq(Base.OperatorMixin, Base.SearchMixin):
    value = datetime(2022, 6, 1)
    operator_checks = lop.LessThenEq(1), [0, 1], 2
    search_checks = DictSearch(match_query={"info": {"departure": {"$lte": value}}}), lambda x: x["info"]["departure"] <= TestLessThenEq.value


class TestIs(Base.OperatorMixin, Base.SearchMixin):
    operator_checks = lop.Is(True), True, False
    search_checks = DictSearch(match_query={"in_route": {"$is": True}}), lambda x: x["in_route"] is True


class TestIn(Base.OperatorMixin, Base.SearchMixin):
    values = [COUNTRY_ARGENTINA, COUNTRY_SPAIN]
    operator_checks = lop.In([1]), 1, 2
    search_checks = DictSearch(match_query={"info": {"origin": {"$in": values}}}), lambda x: x["info"]["origin"] in TestIn.values


class TestNotIn(Base.OperatorMixin, Base.SearchMixin):
    values = [COUNTRY_ARGENTINA, COUNTRY_SPAIN]
    operator_checks = lop.NotIn([1]), 2, 1
    search_checks = DictSearch(match_query={"info": {"origin": {"$nin": values}}}), lambda x: x["info"]["origin"] not in TestNotIn.values


class TestContains(Base.OperatorMixin, Base.SearchMixin):
    value = TAX_B
    operator_checks = lop.Contains(1), {1}, {2}
    search_checks = DictSearch(match_query={"taxes": {"$cont": value}}), lambda x: TestContains.value in x["taxes"]


class TestNotContains(Base.OperatorMixin, Base.SearchMixin):
    value = TAX_B
    operator_checks = lop.NotContains(1), {2}, {1}
    search_checks = DictSearch(match_query={"taxes": {"$ncont": value}}), lambda x: TestNotContains.value not in x["taxes"]


class TestRegex(Base.OperatorMixin, Base.SearchMixin, Base.ExceptionsMixin):
    pattern_str = "^m[ie]+aw"
    value = re.compile(".*01.*", re.IGNORECASE)
    true_args = ["miaw", "mieaw", "mieeeaw", "mieeeaw"]
    false_args = ["miw", "mmieaw", "maw"]
    operator_checks = [
        (lop.Regex(pattern_str), true_args, false_args),
        (lop.Regex(re.compile(pattern_str)), true_args, false_args)
    ]
    search_checks = DictSearch(match_query={"info": {"port_code": {"$regex": value}}}), lambda x: TestRegex.value.search(x["info"]["port_code"])
    exceptions = lambda: lop.Regex(12), exceptions.RegexOperatorException


class TestFunction(Base.OperatorMixin, Base.SearchMixin):
    value = lambda x: sum(x) >= 0.5
    operator_checks = lop.Function(value), [[0.1, 0.2, 0.2], [0.3, 0.2]], [[0.2, 0.2]]
    search_checks = DictSearch(match_query={"taxes": {"$func": value}}), lambda x: TestFunction.value(x["taxes"])


class TestIsInstance(Base.OperatorMixin, Base.SearchMixin):
    value = list
    operator_checks = lop.IsInstance(value), [[]], [{}, 123, "abc", value]
    search_checks = DictSearch(match_query={"port_route": {"$inst": value}}), lambda x: isinstance(x["port_route"], TestIsInstance.value)


class TestCompare(Base.OperatorMixin, Base.SearchMixin, Base.ExceptionsMixin):
    value = 2
    t_keys = ["info", "ship_country"]
    t_func = lambda x, y: y == x
    fixture = {"info": {"ship_country": 2}}
    operator_checks = lop.Compare(t_keys, func=t_func), (value, fixture), (3, fixture)
    search_checks = DictSearch(match_query={"info": {"origin": {"$comp": [t_keys, t_func]}}}), lambda x: x["info"].get("ship_country") == x["info"]["origin"]
    exceptions = [
        (lambda: lop.Compare({}), exceptions.CompOperatorFirstArgError),
        (lambda: lop.Compare([1, {}]), exceptions.CompOperatorFirstArgError),
        (lambda: lop.Compare(1, func=2), exceptions.CompOperatorSecondArgError),
        (lambda: DictSearch(match_query={"$comp": 2}), exceptions.CompOperatorTypeError),
    ]


class TestFind(Base.SearchMixin, Base.ExceptionsMixin):
    value = COUNTRY_MORROCCO
    fixture_data = {"a": {"b": {"c": 12}}, "d": {"e": 34}, "c": 44}
    exceptions = [
        (lambda: lop.Find({1: 2}), Exception),
        (lambda: lop.Find([CursedData()]), Exception),
        (lambda: DictSearch(match_query={"$find": 2}), Exception),
        (lambda: DictSearch(match_query={"$find": [2]}), Exception),
    ]

    def setUp(self) -> None:
        self.search_checks = DictSearch(match_query={"$find": ["ship_country", self.value]}), self.check
        super(TestFind, self).setUp()

    def check(self, x):
        result = find_value(x, "ship_country")
        if isinstance(result, list):
            result = [r.result for r in result]
        else:
            result = result.result
        return self.value == result

    def test_implementation(self):
        assert lop.Find("e")(self.fixture_data) == 34
        assert lop.Find("c")(self.fixture_data) == 12
        assert lop.Find("c", candidates=-1)(self.fixture_data) == [12, 44]
        assert not lop.Find("z")(self.fixture_data)
