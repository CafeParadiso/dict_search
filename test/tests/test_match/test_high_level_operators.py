from datetime import datetime
from unittest import TestCase

from src.dict_search.dict_search import DictSearch
from src.dict_search.operators.operators import high_level_operators as hop
from src.dict_search.operators import get_operators
from src.dict_search.operators import exceptions

from test.utils import BaseTestOperators as Base
from test.new_fixtures.data import COUNTRY_USA, COUNTRY_SPAIN


class TestExceptions(TestCase):
    def test_iterator_error(self):
        for op in get_operators(hop):
            with self.assertRaises(exceptions.HighLevelOperatorIteratorError):
                DictSearch(match_query={"a": {f"${op.name}": (1, 2)}})


class And(Base.OperatorMixin, Base.SearchMixin):
    search = DictSearch({"info": {"$and": [{"origin": COUNTRY_USA}, {"departure": datetime(2022, 6, 1)}]}})
    operator_checks = hop.And(), [[1, 1], [True, True]], [[0, 1], [False, False]]
    search_checks = search, lambda x: x["info"]["origin"] == COUNTRY_USA and x["info"]["departure"] == datetime(2022, 6, 1)

    def test_implicit_and(self):
        data = self.data
        results = list(self.search.filter(data))
        self.assertEqual(
            results,
            list(DictSearch({"info": {"origin": COUNTRY_USA, "departure": datetime(2022, 6, 1)}}).filter(data))
        )


class Or(Base.OperatorMixin, Base.SearchMixin):
    operator_checks = hop.Or(), [[1, 0], [1, 1], [0, 1], [True, False], [True, True], [False, True]], [[0, 0], [False, False]]
    search_checks = DictSearch({"info": {"$or": [{"origin": COUNTRY_USA}, {"departure": datetime(2022, 6, 1)}]}}), lambda x: x["info"]["origin"] == COUNTRY_USA or x["info"]["departure"] == datetime(2022, 6, 1)


class Not(Base.OperatorMixin, Base.SearchMixin):
    operator_checks = hop.Not(), [[0, 1], [1, 0], [True, False], [False, True], [0, 0], [False, False]], [[1, 1], [True, True]]
    search_checks = DictSearch({"info": {"$not": [{"origin": COUNTRY_USA}]}}), lambda x: x["info"]["origin"] != COUNTRY_USA


class NotAny(Base.OperatorMixin, Base.SearchMixin):
    operator_checks = hop.NotAny(), [[0, 0], [False, False]], [[1, 0], [1, 1], [0, 1], [True, False], [True, True], [False, True]]
    search_checks = DictSearch({"info": {"$not_any": [{"origin": COUNTRY_SPAIN}, {"ship_country": COUNTRY_SPAIN}]}}), lambda x: x["info"]["origin"] != COUNTRY_SPAIN and x["info"]["ship_country"] != COUNTRY_SPAIN
